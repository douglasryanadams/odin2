
const form = document.getElementById("search-form");

async function search() {
  const searchForm = new FormData(form);
  const searchTerm = searchForm.get("search-input");

  const searchResponse = await fetch("/api/search", {
    method: "POST",
    body: JSON.stringify({"query": searchTerm })
  });

  if (!searchResponse.ok) {
      throw new Error(searchResponse)
  } else {
      const searchResponseBox = document.getElementById("search-response")
      const searchContentDiv = document.createElement("div")
      searchContentDiv.classList.add("search-results")
      const searchResponseText = document.createTextNode(await searchResponse.json())
      searchContentDiv.appendChild(searchResponseText)
      searchResponseBox.appendChild(searchContentDiv);
  }
}

form.addEventListener(
  "submit", (event) => {
    event.preventDefault();
    search()
  }
);
