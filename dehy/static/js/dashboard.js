$(document).ready(function() {
	// list_items_handler()
});

window.addEventListener('load', function () {
    let item_count = 1;

    function addRemoveEventListener(widgetElement) {
        widgetElement.querySelectorAll('.remove').forEach(element => {
            element.addEventListener('click', () => {
                element.parentNode.remove();
            });
        });
    }

    function initializeWidget(widgetElement) {
        const initialElement = widgetElement.querySelector('.array-item');
        const elementTemplate = initialElement.cloneNode(true);
        const parentElement = initialElement.parentElement;

        if (initialElement.getAttribute('data-isNone')) {
            initialElement.remove();
            elementTemplate.removeAttribute('data-isNone');
            elementTemplate.removeAttribute('style');
        }
        addRemoveEventListener(widgetElement);

        widgetElement.querySelector('.add-array-item').addEventListener('click', () => {
            item_count++;
            const newElement = elementTemplate.cloneNode(true);
            const id_parts = newElement.querySelector('input').getAttribute('id').split('_');
            const id = id_parts.slice(0, -1).join('_') + '_' + String(item_count - 1);
            newElement.querySelector('input').setAttribute('id', id);
            newElement.querySelector('input').value = '';

            addRemoveEventListener(newElement);
            parentElement.appendChild(newElement);
        });
    }

    $(".dynamic-array-widget").not(".empty-form .dynamic-array-widget").each(
        (index, widgetElement) => initializeWidget(widgetElement)
    );

    $(document).on('formset:added', function(event, $row, formsetName) {
        $row[0].querySelectorAll(".dynamic-array-widget").forEach(
            widgetElement => initializeWidget(widgetElement)
        );
    });
	autoslug_handler();

  });

function autoslug_handler() {
	document.querySelectorAll('.autoslug').forEach(function(slug_elem) {
		var elem = document.getElementById(slug_elem.dataset.autoslug)
		elem.addEventListener('change', e=>{
			slug_elem.value = convertToSlug(elem.value)
		})
	})
}

function list_items_handler() {
	var add_more_btn = document.querySelector('button.add_more');
	add_more_btn.addEventListener('click', e=> {
		copy_row_item(e)
	})
	function copy_row_item(e) {
		let template_id = e.target.closest('button').dataset.parent;
		let template = e.target.closest(`div.${template_id}`)
		add_list_item(template, template_id);
	}

	function add_list_item(template_elem, id) {

		var step = template_elem.querySelectorAll('select, input, textarea').length,
			template_copy = template_elem.cloneNode(true),
			form_group = template_elem.closest('div.form-group'),
			field_name = id.replace('id_', '');

		var input_elems = template_copy.querySelectorAll('select, input, textarea')
		input_elems.forEach(function(elem, index) {
			var item_num = parseInt(elem.name.replace(`${field_name}_`, ''))+step
			elem.name = `${field_name}_${item_num}`
			elem.id = `id_${elem.name}`
			if (elem.tagName=='SELECT') {
				elem.selectedIndex = 0;
			} else {
				elem.value = '';
			}

		})

		template_elem.querySelector('button').remove()
		template_copy.querySelector('button').addEventListener('click', copy_row_item)
		form_group.appendChild(template_copy)
	}

}


function convertToSlug(Text) {
	return Text.toLowerCase().replace(/[^\w ]+/g, '').replace(/ +/g, '-');
}

// creates element, textnodes, and attributes, attaches textnode/attributes, returns created element
function create_element(tag, class_name, style, text, dataAttrs = {}) {
	var elem = document.createElement(`${tag}`)
	if (class_name) {
		elem.className = class_name
	}

	if (style) {
		elem.style.cssText = style
	}

	if (text) {
		var content = document.createTextNode(`${text}`);
		elem.appendChild(content)
	}

	if (dataAttrs) {
		for (let [key, val] of Object.entries(dataAttrs)) {
			var dataItem = document.createAttribute(`${key}`);
			dataItem.value = val
			elem.setAttributeNode(dataItem)
		}
	}
	return elem
}