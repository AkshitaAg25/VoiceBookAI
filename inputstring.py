from extractinfo import extract_appointment_info

def run_voicebook():

    # Get the initial request
    firstsen = input("You: ")

    # Keep the original request throughout the conversation
    conversation = firstsen

    while True:

        # Extract information from the full conversation
        result = extract_appointment_info(conversation)

        if result["status"] == "ready":

            details = result["details"]
            # return details
            print("\nExtracted JSON:")
            print(details)

            # Send the completed details to your booking system
            # handle_booking(details)

            break

        elif result["status"] == "missing_info":

            # Ask the user for missing information
            print("\nVoiceBook:", result["message"])

            answer = input("You: ")
            if "the person's name" in result["missing_fields"]:
                conversation += "\nAdditional information: for " + answer
            else:
            # Add the new answer without losing earlier details
                conversation += "\nAdditional information: " + answer

        else:
            print("Sorry, I couldn't process your request.")
            break


if __name__ == "__main__":
    run_voicebook()