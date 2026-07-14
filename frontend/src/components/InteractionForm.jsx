import { useSelector } from "react-redux";


function InteractionForm() {
  const formData = useSelector(
    (state) => state.interaction.formData
  );


  const interactionType = String(
    formData.interaction_type || ""
  ).toLowerCase();


  const sentiment = String(
    formData.sentiment || ""
  ).toLowerCase();


  const attendees = Array.isArray(
    formData.attendees
  )
    ? formData.attendees.join(", ")
    : formData.attendees || "";


  const materialsShared = Array.isArray(
    formData.materials_shared
  )
    ? formData.materials_shared
    : [];


  const samplesDistributed = Array.isArray(
    formData.samples_distributed
  )
    ? formData.samples_distributed
    : [];


  return (
    <main className="interaction-panel">
      <h2>Log HCP Interaction</h2>

      <section className="form-section">
        <h4>Interaction Details</h4>


        <div className="form-grid">
          <div className="field">
            <label>HCP Name</label>

            <input
              value={formData.hcp_name || ""}
              placeholder="Search or select HCP..."
              readOnly
            />
          </div>


          <div className="field">
            <label>Interaction Type</label>

            <select
              value={interactionType}
              disabled
            >
              <option value="">
                Select interaction type
              </option>

              <option value="meeting">
                Meeting
              </option>

              <option value="call">
                Call
              </option>

              <option value="email">
                Email
              </option>

              <option value="conference">
                Conference
              </option>
            </select>
          </div>


          <div className="field">
            <label>Date</label>

            <input
              type="date"
              value={formData.date || ""}
              readOnly
            />
          </div>


          <div className="field">
            <label>Time</label>

            <input
              type="time"
              value={formData.time || ""}
              readOnly
            />
          </div>
        </div>


        <div className="field full">
          <label>Attendees</label>

          <input
            value={attendees}
            placeholder="Enter names or search..."
            readOnly
          />
        </div>


        <div className="field full">
          <label>Topics Discussed</label>

          <textarea
            value={
              formData.topics_discussed || ""
            }
            placeholder="Enter key discussion points..."
            readOnly
          />
        </div>


        <button
          type="button"
          className="voice-button"
          disabled
        >
          🎙 Summarize from Voice Note
          (Requires Consent)
        </button>


        <h4>
          Materials Shared / Samples Distributed
        </h4>


        <div className="summary-row">
          <div>
            <strong>Materials Shared</strong>

            <p>
              {materialsShared.length
                ? materialsShared.join(", ")
                : "No materials added."}
            </p>
          </div>

          <button disabled>
            🔍 Search/Add
          </button>
        </div>


        <div className="summary-row">
          <div>
            <strong>Samples Distributed</strong>

            <p>
              {samplesDistributed.length
                ? samplesDistributed.join(", ")
                : "No samples added."}
            </p>
          </div>

          <button disabled>
            ➕ Add Sample
          </button>
        </div>


        <div
          className="field full sentiment-section"
        >
          <label>
            Observed/Inferred HCP Sentiment
          </label>


          <div className="sentiment-options">
            <label>
              <input
                type="radio"
                name="sentiment"
                checked={
                  sentiment === "positive"
                }
                readOnly
              />

              🙂 Positive
            </label>


            <label>
              <input
                type="radio"
                name="sentiment"
                checked={
                  sentiment === "neutral"
                }
                readOnly
              />

              😐 Neutral
            </label>


            <label>
              <input
                type="radio"
                name="sentiment"
                checked={
                  sentiment === "negative"
                }
                readOnly
              />

              🙁 Negative
            </label>
          </div>
        </div>


        <div className="field full">
          <label>Outcomes</label>

          <textarea
            value={formData.outcomes || ""}
            placeholder="Key outcomes or agreements..."
            readOnly
          />
        </div>


        <div className="field full">
          <label>Follow-up Actions</label>

          <textarea
            value={
              formData.follow_up_actions || ""
            }
            placeholder="Enter follow-up actions..."
            readOnly
          />
        </div>
      </section>
    </main>
  );
}


export default InteractionForm;