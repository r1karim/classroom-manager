selected_channel = null;
document.body.style.zoom = 0.82;
const clean_chatbox = () => {
	const chat_box = $('#channel_display .messagescontainer').first();
	chat_box.html('');
}
const set_chat_title = (server_title,channel_title) => {
	const chat_title = $('#channel_display .upper_part .title').first(); //getting the first h4 element inside of the channel_display element
	chat_title.html(`<b>${server_title}</b> #${channel_title}`);
}
const add_message = (message_data) => {
	const chat_box = $('#channel_display .messagescontainer').first();
	chat_box.append(`<div class="message bg-light"><span><b>${message_data.author.name}</b> ${message_data.date}</span><p>${message_data.content}</p></div>`);
	$(chat_box).scrollTop(10000);
}
const clear_notes = () => {
	const notes = $('#note-container');
	const notes_list = $ ('#note-list');
	notes.html('');
	notes_list.html('');
}
const add_note = (note_data, active) => {
	const note_list = $('#note-list');
	const note_container = $('#note-container');
	let id = note_data.note_title.replaceAll(' ', '') + note_data.note_id.toString(10);
	note_list.append(`<a class="list-group-item list-group-item-action ${active}" data-toggle="list" href="#${id}" role="tab">${note_data.note_title}</a>`);
	note_container.append(`<div class="tab-pane ${active}" id="${id}" role="tabpanel"><img src="${note_data.note_img}" style='max-width:600px; max-height:600px;' /><p>${note_data.note_text}</p></div>`);
}
$(document).ready(function() {
	$('body').click(function(e) {
		var target = $(e.target);
		if(!target.is('#new_conversation_form') && !target.is('#new_conversation_form input')) {
			is_visible = $('#new_conversation_form').css('display');
			if (is_visible != 'none') {
				$('#new_conversation_form').css('display', 'none');
				$('#newconversation').css('display', 'block');
			}
		}
	});
	$(document).on('submit', '#note_form', function(event) {
		let form_data = new FormData($('#note_form')[0]);
		form_data.append('channel_id', selected_channel);
		event.preventDefault();
		if(selected_channel != null) {
			$.ajax({data: form_data,contentType:false, processData:false, url:'add-note', method:'POST'}).done(function(data) {
				$("#note_form").trigger("reset");
				add_note(data['new_note'], '');
			});
		}
	});
	$(document).on('click','#menulist .classroom',function(){
		let id = parseInt($(this).attr('id').slice(1, $(this).attr('id').length), 10);
		$.ajax({url:`retrieve-channels/${id}`, type:'POST'}).done((data) => {
			console.log(data);
			document.getElementsById("OVERLAY").style.height = "100%";
			if(data['result'].length > 0){
				let result = '';
				for(let i = 0; i < data['result'].length; i++) {
					result+= `<li id="%${data['result'][i].id}" class='w3-bar-item w3-button' style='text-decoration: none; width:100%'>${data['result'][i].name}</li>`;
				}
				$('#menulist ul').html('');
				$(this).parent().children('.channels').first().html(result);
			} 
		});
	});
	$(document).on('click', '.channels li', function() {
		let id = parseInt($(this).attr('id').slice(1, $(this).attr('id').length), 10); //getting channel id
		selected_channel = id;
		set_chat_title($(this).parent().parent().children('a').first().html(),$(this).html());
		$.ajax({url:`retrieve-messages/${id}`, type:'POST'}).done((data) => {
			clean_chatbox()
			if (data.result.length) {
				for(let i=0; i < data.result.length; i++) {
					add_message(data.result[i]);
				}
			} else {
				let message = {'author': {'name': 'SC. Bot'}, 'content': 'No messages to display', 'date': 'just now'};
				add_message(message);
			}
		});
		$.ajax({url:`retrieve-notes/${id}`, type:'POST'}).done((data) => {
			console.log(data);
			clear_notes();
			if(data.length) {
				for(let i = 0;i < data.length; i++) {
					if(i == 0) {
						add_note(data[i], 'active');
					}
					else {
						add_note(data[i], '');
					}
				}	
			}
			else {

			}

		});
	});
	$(document).on('click', '#newconversation', function() {
		$('#new_conversation_form').css('display', 'block'); //showing new conversation form
		$('#newconversation').css('display', 'none'); //hiding newconversation button
	});
	$(document).on('keydown', '#new_conversation_form', function(event) {
		if (event.keyCode == 13) {
			event.preventDefault(); //preventing form from submitting
			const user_input = $('#new_conversation_input').val(); //assigning the input to a variable
			$('#new_conversation_input').val(''); //setting input value to empty string
			if (selected_channel != null) {
				socket.emit('channel_conversation', {'channel_id': selected_channel, 'message': user_input});
			}
		}
	});
});
socket.on('channel_conversation', function(data) {
	if(data.channel_id == selected_channel) {
		console.log(data);
		add_message(data);
	}
	else {
		//Code for notification goes here
	}
});
