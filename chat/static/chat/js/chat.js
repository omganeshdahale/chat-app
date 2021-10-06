$(document).ready(function(){
    const chatSocket = new WebSocket(
        'ws://'
        + window.location.host
        + '/ws/chat/'
    );

    chatSocket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        const $msg = $(`<li class="replies">
          <img src="http://emilcarlsson.se/assets/harveyspecter.png" alt="" />
          <p>
            <small class="small d-block mt-2">Harvey Specter | Oct 2, 2021, 8:21 PM</small>
          </p>
        </li>`);
        $msg.find('p').prepend(document.createTextNode(data.message));
        $('#chat-log').append($msg);
    };

    chatSocket.onclose = function(e) {
        console.error('Chat socket closed unexpectedly');
    };
    const $input = $('#chat-message-input');
    const $submit = $('#chat-message-submit');
    $input.focus();
    $input.keyup(function(e) {
        if (e.keyCode === 13) {  // enter, return
            $submit.click();
        }
    });

    $submit.click(function(e) {
        const message = $input.val();
        chatSocket.send(JSON.stringify({
            'message': message
        }));
        $input.val('');
    });
});