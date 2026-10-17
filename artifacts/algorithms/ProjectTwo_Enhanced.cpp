#include <algorithm>
#include <cctype>
#include <fstream>
#include <iostream>
#include <queue>
#include <sstream>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <vector>

using namespace std;

struct Course {
    string courseNumber;
    string courseTitle;
    vector<string> prerequisites;
};

static string trim(const string& text) {
    const size_t first = text.find_first_not_of(" \t\r\n");
    if (first == string::npos) return "";
    const size_t last = text.find_last_not_of(" \t\r\n");
    return text.substr(first, last - first + 1);
}

static string upper(string value) {
    for (char& ch : value) {
        ch = static_cast<char>(toupper(static_cast<unsigned char>(ch)));
    }
    return value;
}

static vector<string> splitCsvLine(const string& line) {
    vector<string> tokens;
    string token;
    stringstream stream(line);
    while (getline(stream, token, ',')) tokens.push_back(trim(token));
    // The course file has plain comma-delimited fields, without quoted commas.
    if (!line.empty() && line.back() == ',') tokens.push_back("");
    return tokens;
}

struct Node {
    Course course;
    Node* left = nullptr;
    Node* right = nullptr;
    explicit Node(const Course& value) : course(value) {}
};

class BinarySearchTree {
    Node* root = nullptr;

    static void destroy(Node* node) {
        if (!node) return;
        destroy(node->left);
        destroy(node->right);
        delete node;
    }

    static void printInOrder(const Node* node) {
        if (!node) return;
        printInOrder(node->left);
        cout << node->course.courseNumber << ", " << node->course.courseTitle << '\n';
        printInOrder(node->right);
    }

public:
    BinarySearchTree() = default;
    BinarySearchTree(const BinarySearchTree&) = delete;
    BinarySearchTree& operator=(const BinarySearchTree&) = delete;
    ~BinarySearchTree() { destroy(root); }

    void clear() {
        destroy(root);
        root = nullptr;
    }

    bool empty() const { return root == nullptr; }

    void insert(const Course& course) {
        Node** current = &root;
        while (*current) {
            if (course.courseNumber < (*current)->course.courseNumber) {
                current = &((*current)->left);
            } else {
                current = &((*current)->right);
            }
        }
        *current = new Node(course);
    }

    const Course* find(const string& courseNumber) const {
        const string target = upper(trim(courseNumber));
        const Node* current = root;
        while (current) {
            if (target == current->course.courseNumber) return &current->course;
            current = target < current->course.courseNumber ? current->left : current->right;
        }
        return nullptr;
    }

    void print() const { printInOrder(root); }
};

class CoursePlanner {
    BinarySearchTree tree;
    vector<Course> courses; // Input order makes equally eligible schedule choices reproducible.
    unordered_map<string, vector<string>> dependents; // prerequisite -> courses unlocked
    unordered_map<string, size_t> initialIndegree;

    static bool buildGraph(const vector<Course>& pending,
                           unordered_map<string, vector<string>>& edges,
                           unordered_map<string, size_t>& indegree,
                           string& error) {
        unordered_set<string> known;
        for (const Course& course : pending) {
            if (!known.insert(course.courseNumber).second) {
                error = "Duplicate course number: " + course.courseNumber;
                return false;
            }
            edges.emplace(course.courseNumber, vector<string>{});
            indegree.emplace(course.courseNumber, 0);
        }

        for (const Course& course : pending) {
            unordered_set<string> seen;
            for (const string& prerequisite : course.prerequisites) {
                if (!known.count(prerequisite)) {
                    error = course.courseNumber + " has an unknown prerequisite: " + prerequisite;
                    return false;
                }
                if (prerequisite == course.courseNumber) {
                    error = course.courseNumber + " cannot require itself.";
                    return false;
                }
                if (!seen.insert(prerequisite).second) {
                    error = course.courseNumber + " repeats prerequisite: " + prerequisite;
                    return false;
                }
                edges[prerequisite].push_back(course.courseNumber);
                ++indegree[course.courseNumber];
            }
        }
        return true;
    }

    static vector<string> topologicalOrder(
        const vector<Course>& pending,
        const unordered_map<string, vector<string>>& edges,
        unordered_map<string, size_t> indegree) {
        queue<string> ready;
        for (const Course& course : pending) {
            if (indegree.at(course.courseNumber) == 0) ready.push(course.courseNumber);
        }
        vector<string> order;
        while (!ready.empty()) {
            string current = ready.front();
            ready.pop();
            order.push_back(current);
            for (const string& next : edges.at(current)) {
                if (--indegree.at(next) == 0) ready.push(next);
            }
        }
        return order;
    }

public:
    bool empty() const { return tree.empty(); }
    const Course* find(const string& courseNumber) const { return tree.find(courseNumber); }
    void printCourseList() const { tree.print(); }

    bool loadFromFile(const string& fileName) {
        ifstream input(fileName);
        if (!input) {
            cout << "Error: Could not open file \"" << fileName << "\".\n";
            return false;
        }
        vector<Course> pending;
        string line;
        size_t lineNumber = 0;
        while (getline(input, line)) {
            ++lineNumber;
            if (trim(line).empty()) continue;
            vector<string> tokens = splitCsvLine(line);
            if (tokens.size() < 2 || tokens[0].empty() || tokens[1].empty()) {
                cout << "Error: Invalid course fields on line " << lineNumber << ".\n";
                return false;
            }
            // The supplied CS 300 file pads rows with empty trailing columns.
            while (tokens.size() > 2 && tokens.back().empty()) tokens.pop_back();
            Course course{upper(tokens[0]), tokens[1], {}};
            for (size_t i = 2; i < tokens.size(); ++i) {
                if (tokens[i].empty()) {
                    cout << "Error: Empty prerequisite on line " << lineNumber << ".\n";
                    return false;
                }
                course.prerequisites.push_back(upper(tokens[i]));
            }
            pending.push_back(course);
        }
        if (pending.empty()) {
            cout << "Error: No courses found.\n";
            return false;
        }

        unordered_map<string, vector<string>> newEdges;
        unordered_map<string, size_t> newIndegree;
        string error;
        if (!buildGraph(pending, newEdges, newIndegree, error)) {
            cout << "Error: " << error << '\n';
            return false;
        }
        if (topologicalOrder(pending, newEdges, newIndegree).size() != pending.size()) {
            cout << "Error: Circular prerequisite dependency detected.\n";
            return false;
        }

        // Commit only after validating the entire file; a bad reload retains old data.
        tree.clear();
        for (const Course& course : pending) tree.insert(course);
        courses = std::move(pending);
        dependents = std::move(newEdges);
        initialIndegree = std::move(newIndegree);
        cout << "Data loaded successfully (" << courses.size() << " courses).\n";
        return true;
    }

    void printRecommendedSchedule() const {
        const vector<string> order = topologicalOrder(courses, dependents, initialIndegree);
        unordered_map<string, string> titles;
        for (const Course& course : courses) titles.emplace(course.courseNumber, course.courseTitle);
        cout << "Recommended prerequisite-respecting order:\n";
        for (size_t i = 0; i < order.size(); ++i) {
            cout << (i + 1) << ". " << order[i] << ", " << titles.at(order[i]) << '\n';
        }
        cout << "This is a prerequisite order, not a term-by-term schedule.\n";
    }
};

static void displayMenu() {
    cout << "1. Load Data Structure.\n"
         << "2. Print Course List (alphanumeric).\n"
         << "3. Print Course.\n"
         << "4. Print Prerequisite-Respecting Order.\n"
         << "9. Exit\n";
}

static bool readMenuChoice(int& choice) {
    string input;
    if (!getline(cin, input)) return false;
    stringstream stream(input);
    if (!(stream >> choice)) return false;
    string extra;
    return !(stream >> extra);
}

int main() {
    CoursePlanner planner;
    cout << "Welcome to the course planner.\n";
    while (cin) {
        displayMenu();
        cout << "What would you like to do? ";
        int choice = 0;
        if (!readMenuChoice(choice)) {
            if (!cin) break;
            cout << "Invalid input.\n";
            continue;
        }
        if (choice == 9) {
            cout << "Thank you for using the course planner!\n";
            break;
        }
        if (choice == 1) {
            cout << "What is the name of the input file? ";
            string fileName;
            if (!getline(cin, fileName)) break;
            planner.loadFromFile(trim(fileName));
            continue;
        }
        if (choice < 2 || choice > 4) {
            cout << choice << " is not a valid option.\n";
            continue;
        }
        if (planner.empty()) {
            cout << "Please load the data file first.\n";
        } else if (choice == 2) {
            cout << "Course list in alphanumeric order:\n";
            planner.printCourseList();
        } else if (choice == 4) {
            planner.printRecommendedSchedule();
        } else {
            cout << "What course do you want to know about? ";
            string courseNumber;
            if (!getline(cin, courseNumber)) break;
            const Course* course = planner.find(courseNumber);
            if (!course) {
                cout << "Course not found.\n";
            } else {
                cout << course->courseNumber << ", " << course->courseTitle << '\n';
                cout << "Prerequisites: ";
                if (course->prerequisites.empty()) cout << "None";
                for (size_t i = 0; i < course->prerequisites.size(); ++i) {
                    if (i) cout << ", ";
                    cout << course->prerequisites[i];
                }
                cout << '\n';
            }
        }
    }
    return 0;
}
