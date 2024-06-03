def prompt_yes_no(message, default=None, modify=True):
    def _modify_message(_message, default):
        if default is None:
            return _message + ' (y/n): '

        if default == True:
            return _message + ' (Y/n): '

        if default == False:
            return _message + ' (y/N): '

    if modify:
        message = _modify_message(message, default)

    answer = input(message)

    if answer.lower() in ['y', 'yes']:
        return True

    if answer.lower() in ['n', 'no']:
        return False

    if answer.lower() in [''] and default is not None:
        return default

    return prompt_yes_no(message, default=default, modify=False)