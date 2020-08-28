// Add event handler for each "Add to Cart" button
//////////////////////////////////////////////////
// get all buttons
var updateBtns = document.getElementsByClassName('update-cart')

for (i = 0; i < updateBtns.length; i++) {
    // add event listener on click for each button
    // set a function to execute on each click
    updateBtns[i].addEventListener('click', function () {
        // display product=product.id and action=add
        var productId = this.dataset.product
        var action = this.dataset.action
        console.log('productId:', productId, 'Action:', action)

        // check if user is authenticated
        console.log('USER:', user)
        if (user == 'AnonymousUser') {
            console.log('User is not authenticated')

        } else {
            updateUserOrder(productId, action)
        }
    })
}

function updateUserOrder(productId, action) {
    console.log('User is authenticated, sending data...')

    // this is the view mtd we want to send data to
    var url = '/update_item/'

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({ 'productId': productId, 'action': action })
    }).then((response) => {
        // acknowledgement in json value
        return response.json();
    }).then((data) => {
        // console that response data out
        // this is what our view is sending out to the template
        console.log('Data:', data)
    });
}