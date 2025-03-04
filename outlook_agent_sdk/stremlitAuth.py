import streamlit as st
from azure.identity import DeviceCodeCredential
from msgraph import GraphServiceClient
from msgraph.generated.models.message import Message
from msgraph.generated.users.item.messages.messages_request_builder import MessagesRequestBuilder

# Azure AD Configuration
CLIENT_ID = "<your-client-id>"
SCOPES = ["User.Read", "Mail.Read"]

# Initialize Azure Identity credential
def get_credential():
    return DeviceCodeCredential(
        client_id=CLIENT_ID,
        client_credential=None,
        tenant_id="common",
        device_code_callback=lambda device_code: st.session_state.update({
            "device_code_info": {
                "message": device_code.message,
                "verification_uri": device_code.verification_uri,
                "user_code": device_code.user_code
            }
        })
    )

# Create Graph client
def get_graph_client(credential):
    return GraphServiceClient(credential, scopes=SCOPES)

# Main app
def main():
    st.title("Microsoft Graph Chat Assistant (SDK Version)")

    # Initialize session state
    if "auth_state" not in st.session_state:
        st.session_state.auth_state = {
            "authenticated": False,
            "graph_client": None,
            "user_info": None,
            "device_code_info": None
        }
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Authentication flow
    if not st.session_state.auth_state["authenticated"]:
        if not st.session_state.auth_state["device_code_info"]:
            # Start device code flow
            credential = get_credential()
            st.session_state.auth_state["graph_client"] = get_graph_client(credential)
            
            # Show device code information
            if "device_code_info" in st.session_state:
                info = st.session_state.device_code_info
                st.write("Please authenticate using:")
                st.write(f"1. Visit: {info['verification_uri']}")
                st.write(f"2. Enter code: {info['user_code']}")
                st.write(info["message"])
        else:
            # Check if authentication completed
            try:
                # Try to get user info to verify authentication
                user = st.session_state.auth_state["graph_client"].me.get()
                st.session_state.auth_state.update({
                    "authenticated": True,
                    "user_info": {
                        "display_name": user.display_name,
                        "email": user.user_principal_name
                    }
                })
                st.rerun()
            except Exception as e:
                st.error(f"Authentication error: {str(e)}")
                st.session_state.auth_state["device_code_info"] = None
        return

    # Chat interface
    if prompt := st.chat_input("What would you like to ask?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Process command
        response = ""
        client = st.session_state.auth_state["graph_client"]
        
        try:
            if "emails" in prompt.lower():
                # Get last 5 emails using SDK
                query_params = MessagesRequestBuilder.MessagesRequestBuilderGetQueryParameters(
                    top=5,
                    select=["subject", "receivedDateTime"]
                )
                request_config = MessagesRequestBuilder.MessagesRequestBuilderGetRequestConfiguration(
                    query_parameters=query_params
                )

                messages = client.me.messages.get(request_configuration=request_config).value
                response = "**Last 5 emails:**\n"
                for msg in messages:
                    response += f"- {msg.subject} ({msg.received_date_time})\n"
            else:
                response = "I can help with Microsoft Graph data. Try asking about your emails!"
        except Exception as e:
            response = f"Error accessing Microsoft Graph: {str(e)}"

        # Display assistant response
        with st.chat_message("assistant"):
            st.markdown(response)
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()