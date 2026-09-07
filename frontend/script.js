const questionInput = document.getElementById("question");
const askButton = document.getElementById("askButton");

const loading = document.getElementById("loading");
const result = document.getElementById("result");
const error = document.getElementById("error");

const statusBadge = document.getElementById("statusBadge");
const answer = document.getElementById("answer");
const reason = document.getElementById("reason");

const sourcesContainer = document.getElementById("sources");
const sourceCount = document.getElementById("sourceCount");
const errorMessage = document.getElementById("errorMessage");


function setQuestion(question) {

    questionInput.value = question;

    questionInput.focus();
}


async function askQuestion() {

    const question = questionInput.value.trim();

    if (!question) {
        alert("Please enter a question.");
        return;
    }


    // Reset UI

    result.classList.add("hidden");
    error.classList.add("hidden");

    loading.classList.remove("hidden");

    askButton.disabled = true;
    askButton.textContent = "Thinking...";


    try {

        const response = await fetch(
            "http://127.0.0.1:8000/ask",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    question: question
                })
            }
        );


        const data = await response.json();


        if (!response.ok) {
            throw new Error(
                data.detail || "Request failed."
            );
        }


        displayResult(data);


    } catch (err) {

        error.classList.remove("hidden");

        errorMessage.textContent = err.message;

    } finally {

        loading.classList.add("hidden");

        askButton.disabled = false;

        askButton.textContent = "Ask";
    }
}


function displayResult(data) {

    result.classList.remove("hidden");


    // Status

    const status = data.status || "UNKNOWN";

    statusBadge.textContent = status;


    statusBadge.className = "status-badge";


    if (status === "ANSWERED") {

        statusBadge.style.background = "#dcfce7";
        statusBadge.style.color = "#166534";

    }

    else if (status === "CONFLICT") {

        statusBadge.style.background = "#fee2e2";
        statusBadge.style.color = "#991b1b";

    }

    else if (status === "NOT_COVERED") {

        statusBadge.style.background = "#fef3c7";
        statusBadge.style.color = "#92400e";

    }

    else {

        statusBadge.style.background = "#e5e7eb";
        statusBadge.style.color = "#374151";
    }


    // Answer

    answer.textContent =
        data.answer || "No answer available.";


    // Reason

    reason.textContent =
        data.reason || "No additional analysis available.";


    // Sources

    const sources = data.sources || [];

    sourceCount.textContent =
        `${sources.length} passage${sources.length === 1 ? "" : "s"}`;


    sourcesContainer.innerHTML = "";


    sources.forEach((source, index) => {

        const card = document.createElement("div");

        card.className = "source-card";


        card.innerHTML = `

            <div class="source-top">

                <span class="section">
                    Passage ${index + 1}
                    • Section ${escapeHTML(source.section)}
                </span>

                <span class="similarity">
                    Similarity: ${source.similarity}
                </span>

            </div>


            <div class="source-info">

                ${escapeHTML(source.title)}
                •
                ${escapeHTML(source.source)}

            </div>


            <div class="passage">

                ${escapeHTML(source.text)}

            </div>
        `;


        sourcesContainer.appendChild(card);

    });


    // Scroll to result

    result.scrollIntoView({
        behavior: "smooth"
    });
}


function escapeHTML(text) {

    const div = document.createElement("div");

    div.textContent = text;

    return div.innerHTML;
}


askButton.addEventListener(
    "click",
    askQuestion
);


questionInput.addEventListener(
    "keydown",
    function(event) {

        if (event.key === "Enter") {
            askQuestion();
        }

    }
);