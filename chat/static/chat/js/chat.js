$(document).ready(function () {
    function getMessage(message, author, author_img_url, datetime) {
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
        return $msg;
    }

    function addChat(chat_pk, name, image_url) {
        const $chat =
            $(`<li id="chat_${chat_pk}" class="contact" data-pk=${chat_pk}>
            <div class="wrap">
              <span class="contact-status busy text-center" style="display: none;"></span>
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
        // move to top
        $("#contacts ul").prepend($(`#chat_${chat_pk}`));

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

        $("#chat-log").append(
            getMessage(message, author, author_img_url, datetime)
        );
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
            $("#chat-log").prepend(
                getMessage(
                    message["message"],
                    message["author"],
                    message["author_img_url"],
                    message["datetime"]
                )
            );
        }
    }

    function fetchedMessages(messages, end_message_pk, initial) {
        if (!messages.length) {
            return;
        }
        loadMessages(messages);
        if (initial) {
            const $messages = $(".messages");
            $messages.scrollTop($messages[0].scrollHeight);
        }
        endMessagePk = end_message_pk;
        blockFetch = false;
    }

    function fetchedChat(chat_pk, name, image_url, detail_url) {
        $(".contact-profile a").text(name);
        $(".contact-profile a").attr("href", detail_url);
        $(".contact-profile img").attr("src", image_url);
        const $chat = $(`#chat_${chat_pk}`);
        $chat.find(".name").text(name);
        $chat.find("img").attr("src", image_url);
    }

    const username = JSON.parse(
        document.getElementById("username").textContent
    );
    let activeChatPk = null;
    let endMessagePk = null;
    let blockFetch = false;
    const chatSocket = new WebSocket(
        "ws://" + window.location.host + "/ws/chat/"
    );

    function removeChat(chat_pk) {
        $(`#chat_${chat_pk}`).remove();
        if (activeChatPk === chat_pk) {
            $(".content").hide();
        }
    }

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
                data["messages"],
                data["end_message_pk"],
                data["initial"]
            );
        } else if (data["command"] === "fetched_chat") {
            fetchedChat(
                data["chat_pk"],
                data["name"],
                data["image_url"],
                data["detail_url"]
            );
        } else if (data["command"] == "remove_chat") {
            removeChat(data["chat_pk"]);
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

        blockFetch = true;
        endMessagePk = null;
        chatSocket.send(
            JSON.stringify({
                command: "fetch_chat",
                chat_pk: activeChatPk,
            })
        );
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

    $(".messages").scroll(function (e) {
        if (!blockFetch && $(this).scrollTop() === 0) {
            blockFetch = true;
            chatSocket.send(
                JSON.stringify({
                    command: "fetch_messages",
                    chat_pk: activeChatPk,
                    end_message_pk: endMessagePk,
                })
            );
        }
    });
});
