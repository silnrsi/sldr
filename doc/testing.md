# Testing

The SLDR uses the pytest framework for its tests.

## Usage

The simplest way to run tests is to run `pytest` or `pytest-3`.

There are command line options to pytest that can help deal with the many
resulting tests (each test function is multiplied by each file). To limit tests
to a single locale use `-L` as in:

```
pytest-3 -L en_US
```

To limit tests to a single test function, use `-k`:

```
pytest-3 -k test_identity
```

## Writing Tests

Test functions can be added to a file starting with a name prefix `test_`. The testing framework will look in such files and find functions starting with the prefix `test_`.
A test function may make use of pytest fixtures. The special fixtures available for the
SLDR are:

| fixture | Description      |
|---------|------------------|
| fixdata | The value of the -F command line option |
| ldml    | A wrapper for the Ldml object for the file under test. It has the following structure:
|         | ldml.ldml - The Ldml object
|         | ldml.dirty - if set by a test, causes the Ldml object to be written back out after all the tests for that file are complete.
|         | ldml.path - Path and filename of the file being tested.
| langid  | The file being tested |


