/* Client script */
document.body.style.zoom = 0.8;

const app_container = $('#app_container');
const app_body = app_container.children("#app_body");
let selected_page = null;
const socket = io.connect('http://' + document.domain + ':' + location.port);
socket.on('connect', function() {
	console.log("Connected to the network server.");
});

$(document).ready(function() {
	$('#mySidebar .w3-bar-item').on('click', function(event) {
		let this_element = this;
		if($(this).attr('name') != selected_page){
			selected_page = $(this).attr('name');
			$.ajax({url: '/app/' + $(this).attr('name'), type: 'POST'}).done(function (data) {
				app_container.html(data);
				$(this_element).addClass('selected_item');
				$('#mySidebar > .w3-bar-item').each(function(index){
					if (this !== this_element){
						$(this).removeClass('selected_item');
					}
				});
			});
		}
	});
	$('#joinclassform').on('submit', function(event) {
		event.preventDefault();

		$.ajax({data: {code: $('#classroom_code').val()}, type:'POST', url:'/join-team'}).done(function(data) {
			if (data.error) {
				console.log(data.error);
				$('#join_notice').css('display', 'block');
				$('#join_notice').html(data.error);
			}
			else {
				$('#menulist').append(`<div><a class="w3-bar-item w3-button classroom" id='%${data.result.id}' style='text-decoration: none; width:100%'><img src="${data.url_for_img}" width=25></img> ${data.result.name} <i class='fas fa-cog float-right'></i></a><ul class="channels"></ul></div>`);
				socket.emit('join-room', data.result.id);
			}
		});
	});
	$('#teamcreationform').on('submit', function(event) {
		$.ajax({
			data: {
				team_name: $('#teamname').val(),
				team_description: $('#teamdescription').val()
			},
			type: 'POST',
			url: '/create-team'
		}).done(function(data) {
			const notice_field = $('#notice');
			if (data.error) {
				notice_field.html(data.error);
				notice_field.addClass('alert-danger');
				notice_field.css('display', 'block');
				console.log("error: team was not created due to the following < " + data.error + " >");
			}
			else {
				notice_field.css('display', 'block');
				notice_field.addClass('alert-success');
				notice_field.html("classroom `" + $('#teamname').val() + "` has been created.");
				socket.emit('join-room', data.new_classroom.id);
				$('#teamname').val('');
				$('#teamdescription').val('');
				setTimeout(() => {
					notice_field.html('');
					notice_field.hide();
					$("#teammodal").hide();
				}, 1624);
				if($('#classrooms').hasClass('selected_item')) {
					$('#menulist').append(`<div><a class='classroom w3-bar-item w3-button' style='text-decoration: none; width:100%' id="%${data.new_classroom.id}"><img src=${data.new_classroom.imgurl} width=25> ${data.new_classroom.name} <i class='fas fa-cog float-right'></i></a><ul class='channels'></ul></div>`);
				}
			}
		});
		event.preventDefault();
	});
});

const toggle_class_creator = () => {
	$('#teammodal').css('display', 'block');
	$('#teammodal').find('.alert').css('display', 'none');
}
const toggle_class_join = () => {
	$('#joinclass_modal').css('display', 'block');
	$('#join_notice').css('display', 'none');
}
const close_settings_menu = () => {
	$('#classroom_settings').css('width', '0%');
}