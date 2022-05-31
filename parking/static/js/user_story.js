document.getElementById('submitplatenum').addEventListener('click', function(e) {
    e.preventDefault();
    console.log("ELO")

    const plateNumberForm = document.getElementById('platenum').value;


    const getTicketAPIEndpoint = '/api/get-ticket';

    fetch(getTicketAPIEndpoint, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({'plate_nr': plateNumberForm}),
        }).then(function (response) {
            switch(response.status_code) {
                case 200:
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
                case 403:
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

function create_payment_div(data) {

    let labelTag = document.createElement("label");
    let buttonTag = document.createElement("input");

    labelTag.setAttribute("for", "submitpayment");
    buttonTag.setAttribute("id", "submitpayment");
    buttonTag.setAttribute("type", "submit");
    buttonTag.setAttribute("value", "Pay");

    labelTag.innerHTML = 'Amount to pay: ' + data["amount"].toString();

    document.getElementById("paymentdiv").append(labelTag, buttonTag);

};


document.getElementById('submitreturnticket').addEventListener('click', function(e) {
    debugger;
    const ticketIDForm = document.getElementById('ticketid').value;
//var x = 2;
//                        window.x=x;
//                        window.piwo=9;
    e.preventDefault();

    const returnTicketAPIEndpoint = '/api/return-ticket';

    fetch(returnTicketAPIEndpoint, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({'ticket_id': ticketIDForm}),
        }).then(function (response) {
            console.log('D*PA')
            switch(response.status) {
                case 200:
                        return response.json()
                    then(function (data) {
                        create_payment_div(data);
                    }).catch(function (error) {

                        console.error(error);
                    });
                    break;
                case 403:
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