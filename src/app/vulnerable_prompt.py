# Example vulnerable code for SecureAI-Scan
# This file is intentionally vulnerable for testing prompt injection detection (AI001)


def vulnerable_prompt(user_input):
    # Directly merging user input into prompt (should trigger AI001)
    prompt = f"You are a secure assistant. User says: {user_input}"
    # Simulate sending to LLM (placeholder)
    print(f"Sending prompt: {prompt}")
    return prompt


if __name__ == "__main__":
    # Example user input that could be malicious
    user_input = input("Enter your message: ")
    vulnerable_prompt(user_input)
