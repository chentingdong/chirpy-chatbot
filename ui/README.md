

# Archetecture

## Functionality Layers
- App
- Bot
- Action
- Service

## UI theming

- Admin

  - Using AdminIndex.vue as routing. Routing base on feature name.

- Bot Designer

  - Using rete as the graphic editor engine

  - BotEditor.vue
    Editing bots

  - BotIntentEditor.vue
    Editing bot meta data

  - BotDebugger.vue
    Debugging the bot while editing

  - BotTesting.vue
    - Testing bots with conversation recorder and player
    - Bulk testing api.


- Simulator

  - to be written into a training room


- Demo pages

  - /demo/:appId

  - Seperate Demo page theming in vue component level, using Index.vue as the routing bot. Routing base on appId.

  - The purpose of this is different page designers can write independent codes.


- Components are shared across admin and designer pages
  - shared
    - Loading
  - for demo pages:
    - CarouselLinks,
    - DataSlides,
    - ImageButtons,
    - ImageSlides,
    - Speech,
    - SimpleTable,
    - TextButtons,
    - Voice,
    - Speech,
    - Debugmessage
  - for admin pages:
    - collapsible (in @/pages/Admin/)

## Running UI in local envinronment
If UI can not start locally, do this:
- `docker-compose -f docker-compose.local.yml run --rm ui bash`
- `rm -rf node_modules/`
- `npm install`
