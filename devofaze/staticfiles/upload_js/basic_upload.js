$(function() {

	// open the file explorer window
	$(".js-upload-photos").click(() => {
		$("#fileupload").click();
	});

	//////////////////////////////
	// upload without progress bar
	//////////////////////////////
	
	// $("#fileupload").fileupload({
	// 	dataType: "json",
	// 	done: (e, data) => {
	// 		console.log(data);
	// 		if (data.result.is_valid) {
	// 			$("#gallery tbody").append(
	// 				"<tr><td><a href='" + data.result.url + "'>" + data.result.name + "</a></td></tr>"
	// 			)
	// 		}
	// 	}
	// })
		
	//////////////////////////////
	// upload with progress bar
	//////////////////////////////
	
	$("#fileupload").fileupload({
		dataType: 'json',

		done: (e, data) => {
			if (data.result.is_valid) {
				$("#gallery tbody").prepend(
					$("img").attr("src",data.result['image-url'])
				)
			}
		}
	})

})