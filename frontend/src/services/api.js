const API_URL = "http://127.0.0.1:8000";


export async function sendAgentMessage(message) {
  const response = await fetch(
    `${API_URL}/agent/chat`,
    {
      method: "POST",

      headers: {
        "Content-Type": "application/json",
      },

      body: JSON.stringify({
        message,
      }),
    }
  );


  if (!response.ok) {
    const errorData = await response.json();

    throw new Error(
      errorData.detail ||
        "AI agent request failed."
    );
  }


  return response.json();
}