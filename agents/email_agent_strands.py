import sys
import os

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print(project_root)
sys.path.insert(0, project_root)

from strands import Agent
from tools.email_tools_strands import generate_email_content, send_email
from config.model_config import get_strands_model

EMAIL_AGENT_PROMPT = """You are an email assistant with capbilities to generate email content and send emails. You can
1. Generate email content based on input context
2. Send emails to recipients

When trying to send an email, you need to provide the recipient's email address, the subject, and the body of the email.
Use generate_email_content to create the email body.
Use send_email to actually send the email.
"""

email_agent = Agent(system_prompt=EMAIL_AGENT_PROMPT, tools=[generate_email_content, send_email], model=get_strands_model())

result = email_agent("Create content for mail to my manager Ramesh to inform him I will not be able to join today due to fever. Do not send the mail.")

print(result)