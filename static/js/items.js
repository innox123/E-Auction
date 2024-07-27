function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

const csrftoken = getCookie("csrftoken");

$(".add-to-watchlist").click(function () {
  let itemId = $(this).data("item-id"); // Get item ID from data attribute
  $.ajax({
    type: "POST",
    url: "/create-watchlist/",
    data: {
      csrfmiddlewaretoken: csrftoken,
      item_id: itemId,
    },
    success: function (data) {
      if (data.success) {
        Toastify({
          text: `${data.message}`,
          duration: 3000,
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
      } else {
        Toastify({
          text: `${data.message}`,
          duration: 3000,
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
      }
    },
    error: function (error) {
      console.error(error.message);
    },
  });
});
