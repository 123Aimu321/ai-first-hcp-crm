import {
  useEffect,
  useRef,
  useState,
} from "react";

import {
  useDispatch,
} from "react-redux";

import {
  Bot,
  Send,
} from "lucide-react";

import {
  sendAgentMessage,
} from "../services/api";

import {
  updateInteractionForm,
} from "../features/interaction/interactionSlice";


function AIAssistant() {
  const dispatch = useDispatch();

  const [message, setMessage] = useState("");

  const [loading, setLoading] = useState(false);

  const chatEndRef = useRef(null);


  const [messages, setMessages] = useState([
    {
      role: "assistant",

      content:
        "Log interaction details here (e.g., 'Met Dr. Smith, discussed Product X efficacy, positive sentiment, shared brochure') or ask for help.",
    },
  ]);


  useEffect(() => {
    chatEndRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages, loading]);


  const handleSend = async () => {
    const text = message.trim();

    if (!text || loading) {
      return;
    }


    setMessages((previous) => [
      ...previous,

      {
        role: "user",
        content: text,
      },
    ]);


    setMessage("");

    setLoading(true);


    try {
      const data = await sendAgentMessage(text);


      console.log(
        "[AI ASSISTANT] Agent response:",
        data
      );


      if (data?.form_update) {
        console.log(
          "[REDUX] Dispatching form update:",
          data.form_update
        );


        dispatch(
          updateInteractionForm(
            data.form_update
          )
        );
      }


      setMessages((previous) => [
        ...previous,

        {
          role: "assistant",

          content:
            data?.response ||
            "Interaction processed successfully.",

          success: Boolean(
            data?.form_update
          ),
        },
      ]);

    } catch (error) {
      console.error(
        "[AI ASSISTANT] Error:",
        error
      );


      setMessages((previous) => [
        ...previous,

        {
          role: "assistant",

          content:
            "Unable to connect to the AI assistant.",
        },
      ]);

    } finally {
      setLoading(false);
    }
  };


  return (
    <aside className="assistant-panel">
      <div className="assistant-header">
        <Bot size={20} />


        <div>
          <h3>AI Assistant</h3>

          <span>
            Log Interaction details here via chat
          </span>
        </div>
      </div>


      <div className="chat-area">
        {messages.map(
          (item, index) => (
            <div
              key={index}
              className={`message ${item.role} ${
                item.success
                  ? "success"
                  : ""
              }`}
            >
              {item.content}
            </div>
          )
        )}


        {loading && (
          <div className="message assistant">
            Analyzing interaction details...
          </div>
        )}


        <div ref={chatEndRef} />
      </div>


      <div className="chat-input">
        <input
          value={message}
          placeholder="Describe interaction..."
          disabled={loading}
          onChange={(event) =>
            setMessage(event.target.value)
          }
          onKeyDown={(event) => {
            if (
              event.key === "Enter" &&
              !event.shiftKey
            ) {
              event.preventDefault();

              handleSend();
            }
          }}
        />


        <button
          type="button"
          onClick={handleSend}
          disabled={loading}
        >
          <Send size={17} />
        </button>
      </div>
    </aside>
  );
}


export default AIAssistant;