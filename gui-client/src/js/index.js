
const form = document.getElementById("search-form");

async function search() {
  const searchForm = new FormData(form);
  const searchTerm = searchForm.get("search-input");

  await fetch("/api/search", {
    method: "POST",
    body: JSON.stringify({"search_term": searchTerm })
  });
}

form.addEventListener(
  "submit", (event) => {
    event.preventDefault();
    search()
  }
);
