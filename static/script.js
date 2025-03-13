function fetchBookDetails() {
    const isbn = document.getElementById("isbn-input").value.trim();
    if (!isbn) {
        alert("Please enter an ISBN.");
        return;
    }

    fetch("/get_book", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ isbn: isbn })
    })
    .then(response => response.json())
    .then(data => {
        const bookResult = document.getElementById("book-result");
        bookResult.innerHTML = "";

        if (data.error) {
            bookResult.innerHTML = `<p class="book-details"><strong>Error:</strong> ${data.error}</p>`;
        } else {
            // Ensure authors & publishers are properly formatted strings
            let authorsText = Array.isArray(data.authors) ? data.authors.join(", ") : data.authors || "N/A";
            let publishersText = Array.isArray(data.publishers) ? data.publishers.join(", ") : data.publishers || "N/A";

            bookResult.innerHTML = `
                ${data.cover_image !== "N/A" ? `<img src="${data.cover_image}" alt="Book Cover" class="book-image">` : ""}
                <div class="book-details">
                    <p><strong>Title:</strong> <span class="uppercase">${data.title}</span> 
                        <button class="copy-btn" onclick="copyText('${escapeText(data.title)}')">📋 Copy</button>
                    </p>
                    <p><strong>Authors:</strong> <span class="uppercase">${authorsText}</span> 
                        <button class="copy-btn" onclick="copyText('${escapeText(authorsText)}')">📋 Copy</button>
                    </p>
                    <p><strong>Publishers:</strong> <span class="uppercase">${publishersText}</span> 
                        <button class="copy-btn" onclick="copyText('${escapeText(publishersText)}')">📋 Copy</button>
                    </p>
                    <p><strong>Publish Date:</strong> ${data.publish_date || "N/A"} 
                        <button class="copy-btn" onclick="copyText('${escapeText(data.publish_date)}')">📋 Copy</button>
                    </p>
                    <p><strong>Edition:</strong> ${data.edition || "N/A"} 
                        <button class="copy-btn" onclick="copyText('${escapeText(data.edition)}')">📋 Copy</button>
                    </p>
                </div>
            `;
        }
    })
    .catch(error => {
        const bookResult = document.getElementById("book-result");
        bookResult.innerHTML = `<p class="book-details"><strong>Error:</strong> Failed to fetch book details. Please try again.</p>`;
        console.error("Error fetching book details:", error);
    });
}

// Function to safely copy text to clipboard
function copyText(text) {
    const tempInput = document.createElement("textarea");
    tempInput.value = text;
    document.body.appendChild(tempInput);
    tempInput.select();
    document.execCommand("copy");
    document.body.removeChild(tempInput);

    alert("Copied to clipboard: " + text);
}

// Escape single quotes to prevent issues in onclick events
function escapeText(text) {
    return text.replace(/'/g, "\\'").replace(/"/g, '\\"');
}
