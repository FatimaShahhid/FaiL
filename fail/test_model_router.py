from fail.core.model_router import choose_model


def main() -> None:
    tests = [
        "Hello FAiL.",
        "What is DNS?",
        "Explain how Microsoft Entra ID authentication works.",
        "Design the architecture for FAiL.",
    ]

    for message in tests:
        choice = choose_model(message)

        print(f"\nRequest: {message}")
        print(f"Model: {choice.model}")
        print(f"Reason: {choice.reason}")


if __name__ == "__main__":
    main()