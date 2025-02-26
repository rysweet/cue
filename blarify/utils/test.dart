class Example {
  // Instance variables
  int _value; // Private variable

  // Constructor
  Example(this._value);

  // Named Constructor
  Example.namedConstructor(this._value) {
    print("Named constructor called!");
  }

  // Factory Constructor
  factory Example.create(int val) {
    return Example(val);
  }

  // Instance Method
  void display() {
    print("Value: $_value");
  }

  // Private Method
  void _privateMethod() {
    print("This is a private method.");
  }

  // Async Method
  Future<void> asyncMethod() async {
    await Future.delayed(Duration(seconds: 1));
    print("Async method executed!");
  }

  // Generator Method (sync)
  Iterable<int> syncGenerator() sync* {
    for (int i = 0; i < _value; i++) {
      yield i;
    }
  }

  // Generator Method (async)
  Stream<int> asyncGenerator() async* {
    for (int i = 0; i < _value; i++) {
      await Future.delayed(Duration(milliseconds: 500));
      yield i;
    }
  }

  // Getter
  int get value => _value;

  // Setter
  set value(int newValue) {
    if (newValue >= 0) {
      _value = newValue;
    } else {
      print("Value cannot be negative");
    }
  }

  // Static Method
  static void staticMethod() {
    print("This is a static method.");
  }

  // Operator Overloading
  Example operator +(Example other) {
    return Example(this._value + other._value);
  }
}

void main() async {
  var ex1 = Example(5);
  ex1.display();

  var ex2 = Example.namedConstructor(10);
  ex2.display();

  var ex3 = Example.create(15);
  ex3.display();

  ex1.value = 20;
  print("Getter value: ${ex1.value}");

  Example.staticMethod();

  var ex4 = ex1 + ex2;
  print("Operator overloaded value: ${ex4.value}");

  await ex1.asyncMethod();

  print("Sync Generator:");
  for (var num in ex1.syncGenerator()) {
    print(num);
  }

  print("Async Generator:");
  await for (var num in ex1.asyncGenerator()) {
    print(num);
  }
}
