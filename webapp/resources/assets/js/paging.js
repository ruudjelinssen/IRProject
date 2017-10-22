class Paging {

	constructor(searchRequest){

		this.pager = document.getElementById('Paging');

		this.pager.addEventListener('click', (event) => {

			this._startPaging(event);
		});
	}

	_startPaging(event){

		const parent = event.target.getParent('nav.Paging');
		if(parent && event.target.get('tag') === 'button'){

			window.scrollTo(0, 0);
			this.searchRequest.setParameter('start', event.target.get('value'));
			UrlHandler.updateSearchUrl(this.searchRequest);
		}
	}

	/**
	 * Set the html to none for all the pagers on the page
	 *
	 * @private
	 */

	_disablePaging(){

		this.pager.innerHTML = '';
	}

	/**
	 * Render the paging template to the screen
	 *
	 * There are 4 distinct cases for desktop devices as to how pagination looks
	 *
	 * All system integers start at 0
	 * All user rendered values are adjusted to account for +1
	 * Parameters that include "start" are a reference to the URL parameter "start"
	 * which determines which result number the page should start from
	 *
	 * @param total - the total number of search results
	 * @private
	 */

	_renderPaging(data){

		const start = data.start;
		const total = data.total.toInt();
		const length = this.searchRequest.length;
		const handlebars = Handlebars.compile($('PagingTemplate').get('html'));
		const template = {};

		// If there are 100 results: 100/10 - 1 = 9 (so from 0, 10 pages in total)

		const total_pages = (total / length).ceil() - 1;
		const current_page = (start / length).toInt();

		let loop_count = total_pages;
		let start_from = 0;

		// Render user centric values

		template.first_number = 1;
		template.last_number = (total_pages + 1).format();
		template.current_page = current_page + 1;
		template.total_results = total.format();
		template.start_result = current_page * 10 + 1;
		template.end_result = Math.min(current_page * 10 + length, total);

		this._renderPortalType(template);

		// Get url start values to go to on certain button clicks

		template.first_start = 0;
		template.last_start = total_pages * length;
		template.next_start = current_page * length + 10;
		template.previous_start = current_page * length - 10;

		// In the complex greater than 8 pages variant, there are 3 cases

		if(total_pages >= 7){

			if(current_page < 5){

				start_from = 0;
				loop_count = 6;
			}

			if(current_page >= 5){

				template.show_spacer_left = true;
				template.show_first = true;
				start_from = current_page - 2;
				loop_count = 4;

				if(current_page > total_pages - 2){

					start_from = total_pages - 4;
				}
			}
		}

		// Enable the previous and next buttons

		template.enable_previous = current_page > 0;
		template.enable_next = current_page < total_pages;

		// Loop over the pages

		template.Pages = [];
		for(let i = 0; i <= loop_count; i++){

			const page_number = start_from + i;
			const item = {};

			item.start = page_number * length;
			item.selected = page_number === current_page;
			item.page = page_number + 1;
			item.four_digits = item.page > 999;

			template.Pages.include(item);
		}

		this.pagers.each(nav => {

			nav.set('html', handlebars(template));
		});
	}
}