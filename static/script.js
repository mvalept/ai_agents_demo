async function sendMessage() {
    const input = document.getElementById("user-input");
    const msg = input.value;
    if (!msg) return;
  
    appendMessage("You", msg);
    input.value = "";
  
    const response = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: msg })
    });
  
    const data = await response.json();
    appendMessage("Agent", data.reply);
  
    // If slots are returned, display clickable buttons
    if (data.slots) {
      const box = document.getElementById("chat-box");
      data.slots.forEach(slot => {
        const btn = document.createElement("button");
        btn.innerText = slot;
        btn.onclick = () => chooseSlot(slot);
        box.appendChild(btn);
      });
    }
  }
  
  async function chooseSlot(slot) {
    appendMessage("You", `I choose: ${slot}`);
    const bookingData = {
      appliance: "fridge",
      issue_summary: "Fridge buzzing, not cooling",
      urgency: "urgent",
      name: "Miguel",
      email: "miguel@example.com",
      phone: "",
      address: "Lisbon, Portugal",
      chosen_slot: slot,
      description: "Fridge is buzzing and not cooling."
    };
  
    const response = await fetch("/book", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(bookingData)
    });
  
    const data = await response.json();
    appendMessage("Agent", data.message);
  }
  
  function appendMessage(sender, text) {
    const box = document.getElementById("chat-box");
    const div = document.createElement("div");
    div.className = sender.toLowerCase();
    div.innerHTML = `<b>${sender}:</b> ${text}`;
    box.appendChild(div);
    box.scrollTop = box.scrollHeight;
  }
  