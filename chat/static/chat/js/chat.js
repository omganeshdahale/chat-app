$(document).ready(function () {
    function addMessage(author, author_img_url, datetime) {
        // add message to chat log
        const dt = new Date(datetime).toLocaleString();
        const source = author === username ? "replies" : "sent";
        const name = author === username ? "You" : author;
        const $msg = $(`<li class="${source}">
          <img src="${author_img_url}" alt="" />
          <p>
            <small class="small d-block mt-2"><span class="name"></span> | ${dt}</small>
          </p>
        </li>`);
        $msg.find("p").prepend(document.createTextNode(message));
        $msg.find(".name").text(name);
        $("#chat-log").append($msg);
    }

    function addChat(chat_pk, name, image_url) {
        const $chat =
            $(`<li id="chat_${chat_pk}" class="contact" data-pk=${chat_pk}>
            <div class="wrap">
              <img src="${image_url}" alt="" />
              <div class="meta">
                <p class="name"></p>
                <p class="preview">No last message</p>
              </div>
            </div>
          </li>`);
        $chat.find(".name").text(name);
        $("#contacts ul").prepend($chat);
    }

    function newMessage(
        chat_pk,
        author,
        author_img_url,
        datetime,
        message,
        unread_messages_count
    ) {
        // update preview
        const name = author === username ? "You" : author;
        $(`#chat_${chat_pk}`).find(".preview").text(`${name}: ${message}`);

        // update unread badge
        if (chat_pk != activeChatPk) {
            const $unread = $(`#chat_${chat_pk} .contact-status.busy`);
            $unread.text(unread_messages_count);
            $unread.show();
            return;
        }

        addMessage(author, author_img_url, datetime);
        const $messages = $(".messages");
        $messages.scrollTop($messages[0].scrollHeight);

        chatSocket.send(
            JSON.stringify({
                command: "read_messages",
                chat_pk: activeChatPk,
            })
        );
    }

    function loadMessages(messages) {
        for (message of messages) {
            addMessage(
                message["author"],
                message["author_img_url"],
                message["datetime"]
            );
        }
    }

    function fetchedMessages(chat_pk, name, image_url, messages) {
        $(".contact-profile p").text(name);
        $(".contact-profile img").attr("src", image_url);
        const $chat = $(`#chat_${chat_pk}`);
        $chat.find(".name").text(name);
        $chat.find("img").attr("src", image_url);
        loadMessages(messages);
        const $messages = $(".messages");
        $messages.scrollTop($messages[0].scrollHeight);
    }

    const username = JSON.parse(
        document.getElementById("username").textContent
    );
    let activeChatPk = null;
    const chatSocket = new WebSocket(
        "ws://" + window.location.host + "/ws/chat/"
    );

    chatSocket.onmessage = function (e) {
        const data = JSON.parse(e.data);

        if (data["command"] === "add_chat") {
            addChat(data["chat_pk"], data["name"], data["image_url"]);
        } else if (data["command"] === "new_message") {
            newMessage(
                data["chat_pk"],
                data["author"],
                data["author_img_url"],
                data["datetime"],
                data["message"],
                data["unread_messages_count"]
            );
        } else if (data["command"] === "fetched_messages") {
            fetchedMessages(
                data["chat_pk"],
                data["name"],
                data["image_url"],
                data["messages"]
            );
        }
    };

    chatSocket.onclose = function (e) {
        console.error("Chat socket closed unexpectedly");
    };

    const $input = $("#chat-message-input");
    const $submit = $("#chat-message-submit");
    $input.keyup(function (e) {
        if (e.keyCode === 13) {
            // enter, return
            $submit.click();
        }
    });

    $submit.click(function (e) {
        const message = $input.val().trim();
        if (message) {
            chatSocket.send(
                JSON.stringify({
                    command: "send_message",
                    chat_pk: activeChatPk,
                    message: message,
                })
            );
            $input.val("");
        }
    });

    $(".contact").click(function (e) {
        if (activeChatPk === $(this).data("pk")) {
            return;
        }

        activeChatPk = $(this).data("pk");
        $(".contact").removeClass("active");
        $(this).addClass("active");
        $(this).find(".contact-status.busy").hide();
        $(".content").show();
        $("#chat-log").empty();
        $input.focus();

        chatSocket.send(
            JSON.stringify({
                command: "fetch_messages",
                chat_pk: activeChatPk,
            })
        );
        chatSocket.send(
            JSON.stringify({
                command: "read_messages",
                chat_pk: activeChatPk,
            })
        );
    });
});
