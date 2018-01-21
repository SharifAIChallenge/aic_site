# Menus Context Processor
these values should be set:
```
ai = {
    'navbar': {
        'link1_title': {
            'address': link1_address,
            'active': True/False
        },
        'link2_title': {
            'address': link2_address,
            'dropdown': {
                'link_title': link_address,
                'link_title': link_address
            }
        }
        ...
    },

    'sidebar': {
        'link1_title': {
            'address': link1_address,
            'active': True/False
        },
        'link2_title': {
            'address': link2_address,
            'dropdown': {
                'link_title': link_address,
                'link_title': link_address
            }
        }
        ...
    }

}
```