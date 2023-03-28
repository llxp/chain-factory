class ArgumentExcluder:
    """
    This class is used to exclude arguments from the arguments dictionary,
    before saving the task in the database
    If the arguments dictionary contains an "exclude" key,
    the values of this key will be excluded from the arguments
    """
    def __init__(self, arguments):
        self.arguments = arguments
        self.arguments_copy = dict(arguments)

    def _argument_excluded(self, argument, excluded_argument):
        return argument != "exclude" and argument == excluded_argument

    def _should_exclude_any_arguments(self):
        return self.arguments and "exclude" in self.arguments

    def _excluded_arguments(self):
        return self.arguments["exclude"]

    def _del_argument(self, argument):
        del self.arguments[argument]

    def _check_exclude_argument(self, argument, excluded_argument):
        if self._argument_excluded(argument, excluded_argument):
            self._del_argument(argument)

    def _exclude_arguments(self):
        for argument in self.arguments_copy:
            for excluded_argument in self._excluded_arguments():
                self._check_exclude_argument(argument, excluded_argument)

    def exclude(self):
        """
        Exclude the arguments from the arguments dictionary
        """
        if self._should_exclude_any_arguments():
            self._exclude_arguments()
