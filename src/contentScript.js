(() => {
  /** Inject the main ReadTheRoom floating action button with badge */
  function ReadTheRoomButton() {
    if (document.getElementById("read-the-room-button")) return;

    const container = document.createElement("div");
    container.id = "read-the-room-button";
    container.style.cssText = `
      position: fixed;
      bottom: 20px;
      right: 20px;
      z-index: 1000;
    `;
    
    const button = document.createElement("button");
    button.innerText = "🔍 ReadTheRoom";
    button.style.cssText = `
      background-color: #ff4500;
      color: white;
      padding: 12px 20px;
      padding-right: 35px; /* Make space for badge */
      border-radius: 50px;
      font-size: 14px;
      border: none;
      cursor: pointer;
      box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.2);
      position: relative; /* For badge positioning */
      transition: background-color 0.2s ease;
    `;

    // Add hover effect
    button.addEventListener('mouseenter', () => {
      button.style.backgroundColor = 'rgb(227, 241, 223)';
      button.style.color = '#000';
    });

    button.addEventListener('mouseleave', () => {
      button.style.backgroundColor = '#ff4500';
      button.style.color = 'white';
    });

    // Create badge
    const badge = document.createElement("div");
    badge.id = "read-the-room-badge";
    badge.style.cssText = `
      position: absolute;
      top: -5px;
      right: -5px;
      background-color: #1a1a1b;
      color: white;
      border-radius: 50%;
      width: 20px;
      height: 20px;
      font-size: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: bold;
      opacity: 0;
      transition: opacity 0.2s ease;
    `;

    button.addEventListener("click", () => {
      console.log("ReadTheRoom button clicked"); // Debug log
      window.postMessage({ type: "OPEN_MODERATOR_PANEL" }, "*");
    });

    button.appendChild(badge);
    container.appendChild(button);
    document.body.appendChild(container);

    // Initial badge update
    updateBadgeCount();
  }

  /** Update the badge count */
  function updateBadgeCount() {
    // Count currently selected buttons on the page
    const selectedButtons = document.querySelectorAll('.add-to-room-button').length > 0 
      ? Array.from(document.querySelectorAll('.add-to-room-button'))
          .filter(button => button.innerText === "✓ Added")
          .length 
      : 0;

    const badge = document.getElementById("read-the-room-badge");
    if (badge) {
      if (selectedButtons === 0) {
        badge.style.opacity = "0";
        // Reset storage when no buttons are selected
        chrome.storage.local.set({ flaggedPosts: {} });
      } else {
        badge.textContent = selectedButtons;
        badge.style.opacity = "1";
      }
    }
  }

  /** Inject "Add to Room" buttons for each Reddit post */
  function AddToRoomButton() {
    document.querySelectorAll(".flat-list.buttons").forEach((post) => {
      if (!post.querySelector(".add-to-room-container")) {
        const postId = post.closest("[data-post-id]")?.dataset.postId ||
          `temp-${Math.random().toString(36).substr(2, 9)}`;

        const button = document.createElement("button");
        button.innerText = "Add to Room";
        button.className = "add-to-room-button";
        button.style.cssText = `
          background-color: #e3f1df;
          color: black;
          padding: 5px 10px;
          border-radius: 20px;
          font-size: 12px;
          border: 1px solid #c3d5bf;
          cursor: pointer;
        `;

        // Get initial state from storage
        chrome.storage.local.get(["flaggedPosts"], (result) => {
          const flaggedPosts = result.flaggedPosts || {};
          if (flaggedPosts[postId]) {
            updateButtonUI(button, true);
          }
        });

        button.addEventListener("click", () => {
          togglePostFlag(postId, button);
        });

        const container = document.createElement("span");
        container.className = "add-to-room-container";
        container.appendChild(button);
        post.appendChild(container);
      }
    });
  }

  /** Toggle post flag state */
  function togglePostFlag(postId, button) {
    chrome.storage.local.get(["flaggedPosts"], (result) => {
      const flaggedPosts = result.flaggedPosts || {};
      const isFlagged = !flaggedPosts[postId];

      flaggedPosts[postId] = isFlagged;
      chrome.storage.local.set({ flaggedPosts });

      chrome.runtime.sendMessage({
        action: "logModeration",
        data: { postId, action: isFlagged ? "flagged" : "unflagged" },
      });

      updateButtonUI(button, isFlagged);
      updateBadgeCount(); // Update badge when post is flagged/unflagged
    });
  }

  /** Update button UI based on state */
  function updateButtonUI(button, isFlagged) {
    button.innerText = isFlagged ? "✓ Added" : "Add to Room";
    button.style.backgroundColor = isFlagged ? "#ff4500" : "#e3f1df";
    button.style.color = isFlagged ? "white" : "black";
  }

  /** Create the side panel */
  function createSidePanel() {
    if (document.getElementById("read-the-room-modal")) return;

    const modal = document.createElement("div");
    modal.id = "read-the-room-modal";
    modal.innerHTML = `
      <div id="chakra-ui-modal" style="
        position: fixed;
        top: 0;
        right: 0;
        width: 400px;
        height: 100%;
        background-color: white;
        box-shadow: -2px 0px 10px rgba(0, 0, 0, 0.2);
        transition: transform 0.3s ease-in-out;
        z-index: 1001;
        display: flex;
        flex-direction: column;
        padding: 20px;
        transform: translateX(100%);
      ">
        <!-- Header with Title and Close Button -->
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #ddd; padding-bottom: 10px;">
          <h3 style="font-size: 18px;">Read the Room</h3>
          <button id="close-modal" style="background: none; border: none; font-size: 18px; cursor: pointer;">✖</button>
        </div>
  
        <!-- Search Bar -->
        <div style="margin-top: 10px; display: flex; align-items: center; border: 1px solid #ccc; border-radius: 6px; padding: 6px;">
          <input type="text" placeholder="Search for past questions/comments" style="border: none; outline: none; flex: 1;">
        </div>
  
        <!-- Tabs -->
        <div style="margin-top: 10px; display: flex; justify-content: space-around; border-bottom: 1px solid #ddd;">
          <button class="tab-button" style="border: none; background: none; font-size: 14px; padding: 10px; cursor: pointer; font-weight: bold;">Queue</button>
          <button class="tab-button" style="border: none; background: none; font-size: 14px; padding: 10px; cursor: pointer;">Flagged</button>
          <button class="tab-button" style="border: none; background: none; font-size: 14px; padding: 10px; cursor: pointer;">Archive</button>
        </div>
  
        <!-- AI Summary Section -->
        <div style="margin-top: 15px; padding: 10px; background: #f8f8f8; border-radius: 6px;">
          <strong>AI Summary</strong>
          <div style="margin-top: 5px; display: flex; align-items: center;">
            <span style="background: #ffcc00; padding: 4px 8px; border-radius: 4px; font-size: 12px;">Publicizing</span>
            <span style="margin-left: 6px; color: green; font-weight: bold;">Very High</span>
          </div>
          <p style="font-size: 12px; color: #555; margin-top: 5px;">This post possibly contains attempts to publicize a legal problem...</p>
        </div>
  
        <!-- Post Content -->
        <div style="margin-top: 15px; padding: 10px; border: 1px solid #ddd; border-radius: 6px;">
          <strong>u/sam040501</strong> <span style="color: gray; font-size: 12px;">• Post • Today, 12:32 PM</span>
          <p style="margin-top: 5px; font-size: 14px;">Facing Legal Trouble with Airbnb in Barcelona, What Should I Do?</p>
          <p style="margin-top: 5px; font-size: 12px; color: #555;">
            I've recently been fined by local authorities in Barcelona for renting out my apartment on Airbnb, which is apparently against new regulations...
          </p>
        </div>
  
        <!-- Moderation Actions -->
        <div style="margin-top: 15px; display: flex; justify-content: space-around;">
          <button class="moderation-button" style="background: #ff4500; color: white; padding: 8px 15px; border-radius: 6px; font-size: 14px; border: none; cursor: pointer;">Remove</button>
          <button class="moderation-button" style="background: #2d89ef; color: white; padding: 8px 15px; border-radius: 6px; font-size: 14px; border: none; cursor: pointer;">Keep</button>
          <button class="moderation-button" style="background: #000; color: white; padding: 8px 15px; border-radius: 6px; font-size: 14px; border: none; cursor: pointer;">Ban User</button>
          <button class="moderation-button" style="background: #6c757d; color: white; padding: 8px 15px; border-radius: 6px; font-size: 14px; border: none; cursor: pointer;">Send Modmail</button>
        </div>
      </div>
    `;

    document.body.appendChild(modal);
    document.getElementById("close-modal").addEventListener("click", hideSidePanel);
  }

  /** Show the side panel */
  function showSidePanel() {
    console.log("Showing side panel"); // Debug log
    if (!document.getElementById('read-the-room-root')) {
      console.log("Creating React root"); // Debug log
      createReactRoot();
    }
    window.postMessage({ type: "OPEN_MODERATOR_PANEL" }, "*");
  }

  /** Hide the side panel */
  function hideSidePanel() {
    document.getElementById("chakra-ui-modal").style.transform = "translateX(100%)";
  }

  function createReactRoot() {
    const root = document.createElement('div');
    root.id = 'read-the-room-root';
    document.body.appendChild(root);
  }

  /** Initialize content script */
  function initialize() {
    createReactRoot(); // Create React root on initialization
    const observer = new MutationObserver(() => {
      AddToRoomButton();
      ReadTheRoomButton();
    });

    observer.observe(document.body, { childList: true, subtree: true });

    // Initial execution
    AddToRoomButton();
    ReadTheRoomButton();
  }

  // Start the content script
  initialize();
})();
  