def ler_arquivo(path: str) -> list[str]:
    with open(path, "r", encoding="utf-8") as file:
        linhas = file.read().splitlines()
    return linhas