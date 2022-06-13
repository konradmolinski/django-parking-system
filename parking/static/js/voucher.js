function create_payment_div(data) {
    amount = data['amount'].toString();
    document.getElementById('paymentdiv').style.display = "block";
    document.getElementById('amountToPayInfo').innerHTML = amount;
};

document.getElementById('submitbutton').addEventListener('click', function(e){

    e.preventDefault();

    const plateNum = document.getElementById('platenum').value;
    const voucherHours = document.getElementById('voucherhours').value;

    const getVoucherAPIEndpoint = '/api/voucher';

    fetch(getVoucherAPIEndpoint, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({'plate_nr': plateNum, 'voucher_hours': voucherHours}),
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
})

document.getElementById('submitpayment').addEventListener('click', function(e){

    e.preventDefault();

    const plateNum = document.getElementById('platenum').value;
    const voucherHours = document.getElementById('voucherhours').value;

    const getVoucherPayAPIEndpoint = '/api/pay-voucher';

    fetch(getVoucherAPIEndpoint, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({'plate_nr': plateNum, 'voucher_hours': voucherHours}),
    }).then(function (response) {
        if (response != 200) {
            console.log(status);
        } else {
            console.log(response);
            return response.json();
        }
    }).catch(function (error) {
        return console.error(error);
    })
})