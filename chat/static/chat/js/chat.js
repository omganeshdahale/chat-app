$(document).ready(function(){
    function addChat(chat_pk, name, image_url){
        const $chat = $(`<li id="chat_${chat_pk}" class="contact" data-pk=${chat_pk}>
            <div class="wrap">
              <img src="${image_url}" alt="" />
              <div class="meta">
                <p class="name"></p>
                <p class="preview">Have you finished the draft on the Hinsenburg deal?</p>
              </div>
            </div>
          </li>`);
        $chat.find('.name').text(name);
        $('#contacts ul').prepend($chat);
    }

    function newMessage(chat_pk, author, author_img_url, datetime, message){
        const name = author === username ? 'You' : author;
        $(`#chat_${chat_pk}`).find('.preview').text(`${name}: ${message}`);

        if (chat_pk === activeChatPk){
            const dt = new Date(datetime).toLocaleString();
            const source = author === username ? 'replies' : 'sent';
            const $msg = $(`<li class="${source}">
              <img src="${author_img_url}" alt="" />
              <p>
                <small class="small d-block mt-2"><span class="name"></span> | ${dt}</small>
              </p>
            </li>`);
            $msg.find('p').prepend(document.createTextNode(message));
            $msg.find('.name').text(name);
            $('#chat-log').append($msg);
        }
    }

    const username = JSON.parse(document.getElementById('username').textContent);
    let activeChatPk = null;
    const chatSocket = new WebSocket(
        'ws://'
        + window.location.host
        + '/ws/chat/'
    );

    chatSocket.onmessage = function(e) {
        const data = JSON.parse(e.data);

        if (data['command'] === 'add_chat') {
            addChat(data['chat_pk'], data['name'], data['image_url']);
        }
        else if (data['command'] === 'new_message') {
            newMessage(
                data['chat_pk'],
                data['author'],
                data['author_img_url'],
                data['datetime'],
                data['message']
            );
        }
    };

    chatSocket.onclose = function(e) {
        console.error('Chat socket closed unexpectedly');
    };

    const $input = $('#chat-message-input');
    const $submit = $('#chat-message-submit');
    $input.keyup(function(e) {
        if (e.keyCode === 13) {  // enter, return
            $submit.click();
        }
    });

    $submit.click(function(e) {
        const message = $input.val().trim();
        if (message){
            chatSocket.send(JSON.stringify({
                'chat_pk': activeChatPk,
                'message': message
            }));
            $input.val('');
        }
    });

    $('.contact').click(function(e){
        if (activeChatPk != $(this).data('pk')){
            activeChatPk = $(this).data('pk');
            $('.content').show();
            $('.contact').removeClass('active');
            $(this).addClass('active');
            $('#chat-log').empty();
            $input.focus();
        }
    });
});