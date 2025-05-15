const pk = JSON.parse(document.getElementById("item_id").textContent);
const username = JSON.parse(document.getElementById("username").textContent);
const start_at = JSON.parse(document.getElementById("start_at").textContent);
const end_at = JSON.parse(document.getElementById("end_at").textContent);
const maxPrice = JSON.parse(document.getElementById("max_price").textContent);
const minPrice = JSON.parse(document.getElementById("min_price").textContent);

const topBidderUsername = document.getElementById("top-bidder-username");
const currentBiddedAmount = document.getElementById("current-bidded-amount");
const numberBids = document.querySelector(".number");
const countdown = document.getElementById("countdown");

const scrollContainer = document.querySelector(".message-body");

// Set the scroll position to the maximum value
scrollContainer.scrollTop = scrollContainer.scrollHeight;


const startAt = new Date(start_at);
const endAt = new Date(end_at);
const now = new Date();



if (now >= startAt) {
  setInterval(() => {
    const now = new Date();
    let timeRemaining;
    if (now < startAt) {
      timeRemaining = startAt - now;
    } else if (now < endAt) {
      // Auction is ongoing
      timeRemaining = endAt - now;
    } else {
      // Auction has ended
      countdown.innerHTML = `<p class='f-14'><i class="bi bi-exclamation-triangle-fill p-r-5 f-18"></i>Auction Is Closed.</p>`;
      return;
    }

    const hours = Math.floor(
      (timeRemaining % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60)
    );
    const minutes = Math.floor(
      (timeRemaining % (1000 * 60 * 60)) / (1000 * 60)
    );
    const seconds = Math.floor((timeRemaining % (1000 * 60)) / 1000);

    countdown.innerHTML = `
            <div class="time-remains">
            <span class="text-danger" >${hours} H</span>
            <span class="text-danger">${minutes} M</span>
            <span class="text-danger">${seconds} S</span>
            </div>
              `;
  }, 1000);
} else {
  countdown.innerHTML =
    "<small class='mb-2 h6'>Auction Not yet Started.</small>";
}



const isSecureConnection = window.location.protocol === "https:";

const webSocketProtocol = isSecureConnection ? "wss://" : "ws://";
const bidSocket = new WebSocket(
  webSocketProtocol + window.location.host + "/ws/items/" + pk + "/"
);

bidSocket.onopen = function (e) {
  console.log("WebSocket connected.");
};

bidSocket.onmessage = (e) => {
  const data = JSON.parse(e.data);
  if (data.error) {
    Toastify({
      text: ` ${data.error}`,
      duration: 7000,
      gravity: "top",
      position: "center",
      className: "info",
      style: {
        background: "#e74a3b",
        color: "#f8f9fc",
        marginTop: "40px",
        fontSize: "1em",
        fontWeight: "600",
        padding: "30px 20px",
        boxShadow: "none",
      },
    }).showToast();
    document.querySelector("#place-bid").innerHTML = "Place Bid Now";
  } else {
    topBidderUsername.innerHTML = `  <i class="fa fa-user-o" aria-hidden="true"></i>  ${data.bidder}`;
    currentBiddedAmount.innerHTML = data.current_amount;
    numberBids.innerHTML = data.number_of_bids;
    document.querySelector("#place-bid").innerHTML = "Place Bid Now";
    if (username === data.bidder) {
          scrollContainer.innerHTML += `<li class="list-group-item bg-primary text-light d-flex justify-content-between align-items-center mb-2">
              <span><i class="fa fa-user-o mr-2" aria-hidden="true"></i>${data.bidder}</span>
               
              <span class="badge badge-primary badge-pill"><i class="fa fa-plus" aria-hidden="true"></i>
             ${data.current_amount} RWF</span>
            </li>`;

          scrollContainer.scrollTop = scrollContainer.scrollHeight;
      Toastify({
        text: `You Place bid to this auctions. vehicle amount ${data.current_amount} RWF`,
        duration: 5000,
        gravity: "bottom",
        position: "right",
        className: "info",
        style: {
          background: "#20c9a6",
          color: "#f8f9fc",
          marginBottom: "20px",
          fontSize: "1em",
          fontWeight: "600",
          padding: "30px 20px",
          boxShadow: "none",
        },
      }).showToast();

    } else {
          scrollContainer.innerHTML += `<li class="list-group-item bg-success text-light d-flex justify-content-between align-items-center mb-2">
              <span><i class="fa fa-user-o mr-2" aria-hidden="true"></i>${data.bidder}</span>
               
              <span class="badge badge-success badge-pill"><i class="fa fa-plus" aria-hidden="true"></i>
             ${data.current_amount} RWF</span>
            </li>`;

          scrollContainer.scrollTop = scrollContainer.scrollHeight;
      Toastify({
        text: `The Bidder throw the bid now amount ${data.current_amount} RWF`,
        duration: 7000,
        gravity: "top",
        position: "center",
        className: "info",
        style: {
          background: "#20c9a6",
          color: "#f8f9fc",
          marginTop: "40px",
          fontSize: "1em",
          fontWeight: "600",
          padding: "30px 20px",
          boxShadow: "none",
        },
      }).showToast();
    }
  }
};

bidSocket.onclose = function (e) {
  console.error("Chat socket closed unexpectedly");
};

document.querySelector("#place-bid").onclick = function () {
  document.querySelector("#place-bid").innerHTML = `
  <span class="f-12" id="bid-loading">
  Bidding
  <svg  xmlns="http://www.w3.org/2000/svg" width="1.5em" height="1.5em" viewBox="0 0 24 24">
	<circle cx="4" cy="12" r="1.5" fill="currentColor">
		<animate attributeName="r" dur="0.75s" repeatCount="indefinite" values="1.5;3;1.5" />
	</circle>
	<circle cx="12" cy="12" r="3" fill="currentColor">
		<animate attributeName="r" dur="0.75s" repeatCount="indefinite" values="3;1.5;3" />
	</circle>
	<circle cx="20" cy="12" r="1.5" fill="currentColor">
		<animate attributeName="r" dur="0.75s" repeatCount="indefinite" values="1.5;3;1.5" />
	</circle>
</svg>
  </span>
  `;
  const amount = document.querySelector("#amount").value;
  if (amount < minPrice) {
    document.querySelector("#place-bid").innerHTML = "Place Bid Now";
    document.querySelector(".item-detail-field-error").style = "display: block";
    setTimeout(function () {
      document.querySelector(".item-detail-field-error").style =
        "display: none";
    }, 2000);
  } else {
    bidSocket.send(
      JSON.stringify({
        amount: amount,
      })
    );
    $("#amount").val("");
  }
};





