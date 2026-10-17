#include <algorithm>
#include <cctype>
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>

using namespace std;

struct Course {
    string courseNumber;
    string courseTitle;
    vector<string> prerequisites;
};

struct Node {
    Course course;
    Node* left;
    Node* right;

    explicit Node(const Course& aCourse) : course(aCourse), left(nullptr), right(nullptr) {}
};

class BinarySearchTree {
private:
    Node* root;

    static string trim(const string& text) {
        size_t start = 0;
        while (start < text.size() && isspace(static_cast<unsigned char>(text[start]))) {
            ++start;
        }

        size_t end = text.size();
        while (end > start && isspace(static_cast<unsigned char>(text[end - 1]))) {
            --end;
        }

        return text.substr(start, end - start);
    }

    static string toUpperCase(string text) {
        for (char& ch : text) {
            ch = static_cast<char>(toupper(static_cast<unsigned char>(ch)));
        }
        return text;
    }

    static vector<string> splitCsvLine(const string& line) {
        vector<string> tokens;
        string token;
        stringstream stream(line);

        while (getline(stream, token, ',')) {
            tokens.push_back(trim(token));
        }

        return tokens;
    }

    static bool courseNumberLess(const string& leftValue, const string& rightValue) {
        return leftValue < rightValue;
    }

    static void destroyTree(Node* node) {
        if (node == nullptr) {
            return;
        }
        destroyTree(node->left);
        destroyTree(node->right);
        delete node;
    }

    void addNode(Node* node, const Course& course) {
        if (courseNumberLess(course.courseNumber, node->course.courseNumber)) {
            if (node->left == nullptr) {
                node->left = new Node(course);
            }
            else {
                addNode(node->left, course);
            }
        }
        else {
            if (node->right == nullptr) {
                node->right = new Node(course);
            }
            else {
                addNode(node->right, course);
            }
        }
    }

    void inOrder(Node* node) const {
        if (node == nullptr) {
            return;
        }

        inOrder(node->left);
        cout << node->course.courseNumber << ", " << node->course.courseTitle << endl;
        inOrder(node->right);
    }

    Course* searchNode(Node* node, const string& courseNumber) const {
        if (node == nullptr) {
            return nullptr;
        }

        string target = toUpperCase(courseNumber);
        string current = toUpperCase(node->course.courseNumber);

        if (target == current) {
            return &(node->course);
        }

        if (target < current) {
            return searchNode(node->left, target);
        }

        return searchNode(node->right, target);
    }

public:
    BinarySearchTree() : root(nullptr) {}

    ~BinarySearchTree() {
        destroyTree(root);
    }

    void clear() {
        destroyTree(root);
        root = nullptr;
    }

    bool isEmpty() const {
        return root == nullptr;
    }

    void insertCourse(const Course& course) {
        if (root == nullptr) {
            root = new Node(course);
        }
        else {
            addNode(root, course);
        }
    }

    Course* searchCourse(const string& courseNumber) const {
        return searchNode(root, courseNumber);
    }

    void printCourseList() const {
        inOrder(root);
    }

    bool loadFromFile(const string& fileName) {
        ifstream inputFile(fileName);
        if (!inputFile.is_open()) {
            cout << "Error: Could not open file \"" << fileName << "\"." << endl;
            return false;
        }

        clear();

        vector<Course> pendingCourses;
        string line;
        int lineNumber = 0;

        while (getline(inputFile, line)) {
            ++lineNumber;

            if (trim(line).empty()) {
                continue;
            }

            vector<string> tokens = splitCsvLine(line);
            if (tokens.size() < 2) {
                cout << "Warning: Skipping invalid line " << lineNumber << "." << endl;
                continue;
            }

            Course course;
            course.courseNumber = toUpperCase(tokens[0]);
            course.courseTitle = tokens[1];

            if (course.courseNumber.empty() || course.courseTitle.empty()) {
                cout << "Warning: Skipping invalid line " << lineNumber << "." << endl;
                continue;
            }

            for (size_t i = 2; i < tokens.size(); ++i) {
                if (!tokens[i].empty()) {
                    course.prerequisites.push_back(toUpperCase(tokens[i]));
                }
            }

            pendingCourses.push_back(course);
        }

        inputFile.close();

        for (const Course& course : pendingCourses) {
            insertCourse(course);
        }

        for (const Course& course : pendingCourses) {
            for (const string& prerequisite : course.prerequisites) {
                if (searchCourse(prerequisite) == nullptr) {
                    cout << "Warning: " << course.courseNumber
                         << " has an invalid prerequisite: " << prerequisite << endl;
                }
            }
        }

        cout << "Data loaded successfully." << endl;
        return true;
    }
};

static void displayMenu() {
    cout << "1. Load Data Structure." << endl;
    cout << "2. Print Course List." << endl;
    cout << "3. Print Course." << endl;
    cout << "9. Exit" << endl;
}

static bool readMenuChoice(int& choice) {
    string input;
    getline(cin, input);

    if (input.empty()) {
        return false;
    }

    stringstream stream(input);
    stream >> choice;

    return !stream.fail() && stream.eof();
}

static void printCourseInformation(BinarySearchTree& bst) {
    cout << "What course do you want to know about? ";
    string courseNumber;
    getline(cin, courseNumber);

    Course* course = bst.searchCourse(courseNumber);
    if (course == nullptr) {
        cout << "Course not found." << endl;
        return;
    }

    cout << course->courseNumber << ", " << course->courseTitle << endl;

    cout << "Prerequisites: ";
    if (course->prerequisites.empty()) {
        cout << "None" << endl;
        return;
    }

    for (size_t i = 0; i < course->prerequisites.size(); ++i) {
        cout << course->prerequisites[i];
        if (i < course->prerequisites.size() - 1) {
            cout << ", ";
        }
    }
    cout << endl;
}

int main() {
    BinarySearchTree courseTree;
    string fileName;
    int choice = 0;

    cout << "Welcome to the course planner." << endl;

    while (choice != 9) {
        displayMenu();
        cout << "What would you like to do? ";

        if (!readMenuChoice(choice)) {
            cout << "Invalid input." << endl;
            continue;
        }

        switch (choice) {
        case 1:
            cout << "What is the name of the input file? ";
            getline(cin, fileName);
            courseTree.loadFromFile(fileName);
            break;

        case 2:
            if (courseTree.isEmpty()) {
                cout << "Please load the data file first." << endl;
            }
            else {
                cout << "Here is a sample schedule:" << endl;
                courseTree.printCourseList();
            }
            break;

        case 3:
            if (courseTree.isEmpty()) {
                cout << "Please load the data file first." << endl;
            }
            else {
                printCourseInformation(courseTree);
            }
            break;

        case 9:
            cout << "Thank you for using the course planner!" << endl;
            break;

        default:
            cout << choice << " is not a valid option." << endl;
            break;
        }
    }

    return 0;
}
