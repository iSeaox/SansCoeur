document.addEventListener("DOMContentLoaded", function () {
  const titleElement = document.querySelector(".title");
  const text = titleElement.textContent;
  titleElement.innerHTML = "";
  for (let i = 0; i < text.length; i++) {
    const span = document.createElement("span");
    span.textContent = text[i] === " " ? "\u00A0" : text[i];
    span.style.setProperty("--i", i);
    titleElement.appendChild(span);
  }

  const forgotLink = document.querySelector(".login-forgot");
  forgotLink.addEventListener("click", function (e) {
    e.preventDefault();

    let toastContainer = document.getElementById("toast-container");
    if (!toastContainer) {
      toastContainer = document.createElement("div");
      toastContainer.id = "toast-container";
      document.body.appendChild(toastContainer);
    }

    const toast = document.createElement("div");
    toast.className = "toast align-items-center text-bg-info border-0 mb-2";
    toast.setAttribute("role", "alert");
    toast.setAttribute("aria-live", "assertive");
    toast.setAttribute("aria-atomic", "true");
    toast.innerHTML = `
      <div class="d-flex">
        <div class="toast-body">CHEHHHHH</div>
        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
      </div>
    `;
    toastContainer.appendChild(toast);
    const bsToast = new bootstrap.Toast(toast, { delay: 2000 });
    bsToast.show();
    toast.addEventListener("hidden.bs.toast", function () {
      toast.remove();
    });
  });
});
