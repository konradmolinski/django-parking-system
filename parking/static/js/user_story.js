document.getElementById('submitplatenum').addEventListener('click', function(e) {

    const plateNumberForm = document.getElementById('platenum').value;

    e.preventDefault();

    const host = '/api/ticket-machine';

    const status200 = "{{200}}";
    const status403 = "{{403}}";

    fetch(host, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({'plate_nr': plateNumberForm}),
        }).then(function (response) {
            switch(response.status_code) {
                case status200:
                    console.log("SUCCESS")
                    .then(function (response) {
                        console.log(response)
                        return response
                    }).then(function (response) {
                        return response.json();
                    }).catch(function (error) {
                        console.error(error);
                    });
                    break;
                case status403:
                    console.log("Not Successful")
                    .then(function (response) {
                        console.log(response)
                        return response
                    }).then(function (response) {
                        return response.status;
                    }).catch(function (error) {
                        console.error(error);
                    });
            }
        });
    });