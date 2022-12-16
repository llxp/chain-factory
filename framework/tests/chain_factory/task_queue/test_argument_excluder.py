from framework.src.chain_factory.task_queue.argument_excluder import ArgumentExcluder  # noqa: E501


def test_argument_excluder():
    arguments = {
        "exclude": ["exclude1", "exclude2"],
        "exclude1": "exclude1",
        "exclude2": "exclude2",
        "exclude3": "exclude3",
        "exclude4": "exclude4",
    }
    argument_excluder = ArgumentExcluder(arguments)
    argument_excluder.exclude()
    assert "exclude1" not in argument_excluder.arguments
    assert "exclude2" not in argument_excluder.arguments
    assert "exclude3" in argument_excluder.arguments
    assert "exclude4" in argument_excluder.arguments
