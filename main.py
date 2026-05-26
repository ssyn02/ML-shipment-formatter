from auth.login import get_tokens
from parser import run_parser

def main():
    tokens = get_tokens()
    run_parser(tokens)
    print("Terminado.")

if __name__ == "__main__":
    main()