const form = document.getElementById('OrderingForm');
const orderingSelect = document.getElementsByClassName('js-orderingSelect')[0];
orderingSelect.addEventListener('change', () => {
	form.submit();
});