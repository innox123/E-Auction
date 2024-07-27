$(document).ready(function () {
  $("#msform").on("submit", function () {
    $("#submit-btn").addClass("disabled");
    $("#btn-content").css({
      display: "none",
    });
    $(".loader").css({
      display: "block",
    });
  });
});

$(document).ready(function () {
  var current_fs, next_fs, previous_fs;
  var opacity;

  $(".next").click(function () {
    current_fs = $(this).parent();
    next_fs = $(this).parent().next();

    // Validate all required fields in the current fieldset
    var valid = true;
    current_fs.find("input[required]").each(function () {
      if ($(this).val() === "") {
        valid = false;
        $(this).addClass("is-invalid");
      } else {
        $(this).removeClass("is-invalid");
      }
    });

    if (valid) {
      // Add Class Active
      $("#progressbar li").eq($("fieldset").index(next_fs)).addClass("active");

      // Show the next fieldset
      next_fs.show();
      // Hide the current fieldset with style
      current_fs.animate(
        { opacity: 0 },
        {
          step: function (now) {
            // For making fieldset appear animation
            opacity = 1 - now;

            current_fs.css({
              display: "none",
              position: "relative",
            });
            next_fs.css({ opacity: opacity });
          },
          duration: 800,
        }
      );
    } else {
      alert("Please fill out all required fields.");
    }
  });

  $(".previous").click(function () {
    current_fs = $(this).parent();
    previous_fs = $(this).parent().prev();

    // Remove class active
    $("#progressbar li")
      .eq($("fieldset").index(current_fs))
      .removeClass("active");

    // Show the previous fieldset
    previous_fs.show();

    // Hide the current fieldset with style
    current_fs.animate(
      { opacity: 0 },
      {
        step: function (now) {
          // For making fieldset appear animation
          opacity = 1 - now;

          current_fs.css({
            display: "none",
            position: "relative",
          });
          previous_fs.css({ opacity: opacity });
        },
        duration: 600,
      }
    );
  });
});

$("#reset").click(function () {
  location.reload();
});


