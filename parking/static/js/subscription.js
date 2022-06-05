function create_payment_div(data) {

    amount = data['amount'].toString();
    document.getElementById('paymentdiv').style.display = "block";
    document.getElementById('amountToPayInfo').innerHTML = amount;

//    payEventListener();

    };


document.getElementById('submitbutton').addEventListener('click', function(e) {
    e.preventDefault();

    const plateNum = document.getElementById('platenum').value;
    const startDate = document.getElementById('substartdate').value;
    const endDate = document.getElementById('subenddate').value;

    const getSubscriptionAPIEndpoint = '/api/subscription';

    fetch(getSubscriptionAPIEndpoint, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({'plate_nr': plateNum, 'start_date': startDate, 'end_date': endDate}),
        }).then(function (response) {
            if (response.status != 200){
                console.log(status)
            }
            else {
                console.log(response)
                return response
            }
        }).then(function (response) {
            return response.json();
        }).then(function (data) {
            create_payment_div(data);
        }).catch(function (error) {
            console.error(error);
        });
    });

    document.getElementById('submitpayment').addEventListener('click', function(e) {
        e.preventDefault();

        const plateNum = document.getElementById('platenum').value;
        const startDate = document.getElementById('substartdate').value;
        const endDate = document.getElementById('subenddate').value;

        const payAPIEndpoint = '/api/pay-sub';

        fetch(payAPIEndpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({'start_date': startDate, 'end_date': endDate, 'plate_nr': plateNum}),
            }).then(function (response) {
                if (response.status != 200){
                    console.log(status)
                    return response;
                }
                else {
                    console.log(response)
                    return response.json();
                }
            }).catch(function (error) {
                console.error(error);
            });
        });


document.getElementById('substartdate').addEventListener('change', function(e) {

    const endDate = document.getElementById('subenddate');
    endDate.min = e.target.value;
    endDate.value = e.target.value;

    let d = new Date(e.target.value);
    d = new Date(d.getTime() + 1000*3600*24*28);

    let value = String(d.getFullYear());
    const month = d.getMonth() + 1;
    const day = d.getDate() + 1;

    if (month >= 10) {
        value += "-" + String(month);
    } else {
        value += "-0" + String(month);
    }
    if (day >= 10) {
        value += "-" + String(day);
    } else {
        value += "-0" + String(day);
    }

    endDate.setAttribute('max', value);

});
