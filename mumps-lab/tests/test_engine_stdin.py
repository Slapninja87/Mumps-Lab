from harness.engine import run_routine


def write_routine(directory, name, body):
    (directory / f"{name}.m").write_text(f"{name} ;\n{body}", encoding="utf-8")


def test_stdin_text_feeds_a_read_command(tmp_path):
    write_routine(tmp_path, "greet", ' read "Name: ",name,!\n write "Hi ",name,!\n quit\n')

    result = run_routine("greet", tmp_path, stdin_text="Michael\n")

    assert result.stdout == "Name: \nHi Michael\n"


def test_read_past_the_end_of_piped_input_returns_empty_instead_of_hanging(tmp_path):
    write_routine(tmp_path, "greedy", ' read "A: ",a,!\n read "B: ",b,!\n write "[",b,"]",!\n quit\n')

    result = run_routine("greedy", tmp_path, stdin_text="only one line\n", timeout=10)

    assert result.returncode == 0
    assert "[]" in result.stdout
