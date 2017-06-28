/**
 * Contains the class definition and implementation of a circular doubly
 * linked list. 
 * 
 * @author George Miller
 * @file List.h
 * @date April 9, 2011
 */

#include<iostream>
#include<stdexcept>
#include<new>

#ifndef LIST_H
#define LIST_H

/**
 * Implements a templated doubly linked circular list. With built-in methods
 * to sort and print the entire list.
 */
template <class ListItemType>
class List {

public:

    List();
    List(List<ListItemType> & original);
    ~List();

    bool isEmpty() const;

    int getLength() const;

    void insert(int index, const ListItemType &value);
    void printForward() const;
    void printReverse() const;
	void remove(int index);
    void swap(int index1, int index2);
    void sort();

    ListItemType retrieve(int index) const;

private:
    struct Node {
        ListItemType data;
        Node * prev;
        Node * next;
    };

    Node * head;
    int size;

    Node * findForward(int index) const {

        Node * ptr = head;

        if (index == 1) {
            return ptr;
		}

        for (int i = 1; i < index; i++) {
            ptr = ptr -> next;
		}

        return ptr;
    }

    Node * findReverse(int index) const {

        Node * ptr = head -> prev;

        int temp = getLength() - index;

        if (temp == 0) {
            return ptr;
		}

        for (int i = temp; i > 0; i--) {
            ptr = ptr -> prev;
		}

        return ptr;
    }
};

/**
 * Default constructor.
 */
template <class ListItemType>
List<ListItemType>::List() {

    head = NULL;
    size = 0;
}

/**
 * Copy constructor.
 */
template <class ListItemType>
List<ListItemType>::List(List<ListItemType> & original) {

    this -> head = NULL;
    this -> size = 0;

    for (int i = 1; i <= original.getLength(); i++) {
        this -> insert(i, original.retrieve(i));
	}
}

/**
 * Default destructor.
 */
template <class ListItemType>
List<ListItemType>::~List() {

    while (!isEmpty())
        remove(1);
}

/**
 * Returns true if the list has no elements.
 *
 * @pre An initialized list.
 * @return True if the list is empty.
 */
template <class ListItemType>
bool List<ListItemType>::isEmpty() const {

    return size == 0;
}

/**
 * Returns the number of elements in the list.
 *
 * @return The current length of the list.
 */
template <class ListItemType>
int List<ListItemType>::getLength() const {

    return size;
}

/**
 * Inserts an element at the desired index in the list.
 *
 * @param index The index where the item should be placed index can be
 *              any value from 1 to the length of the list + 1.
 * @param value The item that will be placed at the desired index.
 * @pre None.
 * @post A list with the item placed at the given index.
 */
template <class ListItemType>
void List<ListItemType>::insert(int index, const ListItemType & value) {

    try {
        if (index < 1 || index > getLength() + 1) {
            throw std::out_of_range("List index out of range.");
		}

        Node * ptr = new Node;
        ptr -> data = value;

        if (index == 1) {
            if (getLength() == 0) {
                head = ptr;
                ptr -> next = ptr -> prev = head;
            }
            else {
                ptr -> next = head;
                ptr -> prev = head -> prev;
                head -> prev -> next = ptr;
                head -> prev = ptr;
                head = ptr;
            }
        }
        else {

            Node * cur;

            if (index < getLength()/2)
                cur = findForward(index);
            else
                cur = findReverse(index);

            ptr -> next = cur -> next;
            ptr -> prev = cur;
            cur -> next -> prev = ptr;
            cur -> next = ptr;
        }
        size++;
    }
    catch (std::out_of_range re) {
        std::cout << re.what() << std::endl;
    }
    catch (std::bad_alloc) {
        std::cout << "Out of memory." << std::endl;
    }
}

/**
 * Removes the item at the specified index.
 *
 * @param index The index of the desired element.
 * @pre A list with at least one element.
 * @post The list with the element at the desired index removed.
 */
template <class ListItemType>
void List<ListItemType>::remove(int index) {

    try {
        if (getLength() == 0) {
            throw std::logic_error("Cannot remove from empty list.");
		}
        if (index < 1 || index > getLength()) {
            throw std::out_of_range("List index out of range.");
		}

        Node * ptr;

        if (index < getLength()/2) {
            ptr = findForward(index);
		}
        else {
            ptr = findReverse(index);
		}

        if (index == 1) {
            head = head -> next;
            head -> prev = ptr -> prev;
            ptr -> prev -> next = head;
        }
        else {
            Node * cur;

            if (index < getLength()/2) {
                cur = findForward(index - 1);
			}
            else {
                cur = findReverse(index - 1);
			}

            cur -> next = ptr -> next;
            ptr -> next -> prev = cur;
        }

        ptr -> next = ptr -> prev = NULL;
        delete ptr;
        ptr = NULL;

        size--;
    }
    catch (std::out_of_range re) {
        std::cout << re.what() << std::endl;
    }
    catch (std::logic_error le) {
        std::cout << le.what() << std::endl;
    }
}

/**
 * Prints the entire list from the beginning.
 *
 * @pre None
 * @post The list is printed with items separated by spaces with the item
 *       at the first index before the second index etc.
 */
template <class ListItemType>
void List<ListItemType>::printForward() const {

    try {
        if (isEmpty()) {
            throw std::logic_error("Empty list.");
		}

        for (int i = 1; i <= getLength(); i++) {
            std::cout << findForward(i) -> data << ' ';
		}
    }
    catch (std::logic_error le) {
        std::cout << le.what() << std::endl;
    }
}

/**
 * Prints the entire list in reverse order.
 *
 * @pre None
 * @post The list is printed with the items separated by spaces with the item
 *       at the last index before the next to last index etc.
 */
template <class ListItemType>
void List<ListItemType>::printReverse() const {

    try {
        if (isEmpty()) {
            throw std::logic_error("Empty list.");
		}

        for (int i = getLength(); i >= 1 ; i--) {
            std::cout << findReverse(i) -> data << ' ';
		}
    }
    catch (std::logic_error le) {
        std::cout << le.what() << std::endl;
    }
}

/**
 * Swaps the items at the desired indices.
 *
 * @param index1 The index of the first item.
 * @param index2 The index of the second item.
 * @pre A list with at least two elements.
 * @post A list with items at both indices swapped.
 */
template <class ListItemType>
void List<ListItemType>::swap(int index1, int index2) {

    try {
        if (getLength() < 2) {
            throw std::out_of_range("Cannot swap, list is too small.");
		}
        if (index1 < 1 || index1 > getLength()) {
            throw std::out_of_range("Index 1 is out of range.");
		}
        if (index2 < 1 || index2 > getLength()) {
            throw std::out_of_range("Index 2 is out of range.");
		}

        Node * first, * second;
        ListItemType temp;

        if (index1 < getLength()/2){
            first = findForward(index1);
		}
        else {
            first = findReverse(index1);
		}
        if (index2 < getLength()/2) {
            second = findForward(index2);
		}
        else {
            second = findReverse(index2);
		}

        temp = first -> data;
        first -> data = second -> data;
        second -> data = temp;
    }
    catch (std::out_of_range re) {
        std::cout << re.what() << std::endl;
    }

}

/**
 * Implements selection sort.
 *
 * @pre A list with at least two elements.
 * @post A fully sorted list with the least element at the front, and
 *       the greatest element at the end.
 */
template <class ListItemType>
void List<ListItemType>::sort() {

    try{
        if(getLength() < 2) {
            throw std::logic_error("List is already sorted.");
		}

        int min, curr;
        for(curr = 1; curr <= getLength(); curr++){

            min = curr;

            for(int i = curr + 1; i <= getLength(); i++){

                if(findForward(i) -> data < findForward(min) -> data){
                    min = i;
                }
            }
            if(min != curr) {
                swap(curr, min);
			}
        }
        
    }
    catch(std::logic_error le){
        std::cout << le.what() << std::endl;
    }

}

/**
 * Returns the item at the index.
 *
 * @param index The index of the desired element.
 * @pre A list with at least one element.
 * @post The item at the desired index is returned.
 * @return The item at the desired index in the list.
 */
template <class ListItemType>
ListItemType List<ListItemType>::retrieve(int index) const {

    try {
        if (index > getLength() || index < 1) {
            throw std::out_of_range("Index out of range.");
		}

        Node * ptr;

        if (index < getLength()/2) {
            ptr = findForward(index);
		}
        else {
            ptr = findReverse(index);
		}

        return ptr -> data;
    }
    catch (std::out_of_range re) {
        std::cout << re.what() << std::endl;
    }
}

#endif
