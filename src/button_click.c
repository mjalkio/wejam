#include <pebble.h>
#include <string.h>
#define NUM_MENU_SECTIONS 1
#define NUM_MENU_ICONS 1
#define NUM_FIRST_MENU_ITEMS 1

  
static MenuLayer *s_menu_layer;
static Window *window;
static TextLayer *text_layer;
static GBitmap *s_example_bitmap;
static BitmapLayer *s_bitmap_layer;
static GBitmap *s_menu_icons[NUM_MENU_ICONS];
//Maybe needs to be taken out
static GBitmap *s_background_bitmap;
static int s_current_icon = 0;

//MENU SHIT
static uint16_t menu_get_num_sections_callback(MenuLayer *menu_layer, void *data) {
  return NUM_MENU_SECTIONS;
}

static uint16_t menu_get_num_rows_callback(MenuLayer *menu_layer, uint16_t section_index, void *data) {
  return NUM_FIRST_MENU_ITEMS;
}
static int16_t menu_get_header_height_callback(MenuLayer *menu_layer, uint16_t section_index, void *data) {
  return MENU_CELL_BASIC_HEADER_HEIGHT;
}

static void menu_draw_header_callback(GContext* ctx, const Layer *cell_layer, uint16_t section_index, void *data) {
    // Draw title text in the section header
    menu_cell_basic_header_draw(ctx, cell_layer, "Current Playlist");
}

static void menu_draw_row_callback(GContext* ctx, const Layer *cell_layer, MenuIndex *cell_index, void *data) {
      // Use the row to specify which item we'll draw
      switch (cell_index->row) {
        case 0:
          // This is a basic menu item with a title and subtitle
          menu_cell_basic_draw(ctx, cell_layer, "Playlists", "Click to see Playlists", NULL);
          break;
      }
}

static void menu_select_callback(MenuLayer *menu_layer, MenuIndex *cell_index, void *data) {
  // Use the row to specify which item will receive the select action
  switch (cell_index->row) {
    // This is the menu item with the cycling icon
    case 1:
      // Cycle the icon
      s_current_icon = (s_current_icon + 1) % NUM_MENU_ICONS;
      // After changing the icon, mark the layer to have it updated
      layer_mark_dirty(menu_layer_get_layer(menu_layer));
      break;
  }
}

static void select_click_handler(ClickRecognizerRef recognizer, void *context) {
  //text_layer_set_text(text_layer, "Ukasbfb");
  // Destroy output TextLayer
  text_layer_destroy(text_layer);
  bitmap_layer_destroy(s_bitmap_layer);
  gbitmap_destroy(s_example_bitmap);
  
  menu_layer_set_callbacks(s_menu_layer, NULL, (MenuLayerCallbacks){
    .get_num_sections = menu_get_num_sections_callback,
    .get_num_rows = menu_get_num_rows_callback,
    .get_header_height = menu_get_header_height_callback,
    .draw_header = menu_draw_header_callback,
    .draw_row = menu_draw_row_callback,
    .select_click = menu_select_callback,
  });
  menu_layer_set_click_config_onto_window(s_menu_layer, window);
}

static void up_click_handler(ClickRecognizerRef recognizer, void *context) {
  text_layer_set_text(text_layer, "Upvoted!");
}

static void down_click_handler(ClickRecognizerRef recognizer, void *context) {
  text_layer_set_text(text_layer, "Downvoted!");
}

static void click_config_provider(void *context) {
  window_single_click_subscribe(BUTTON_ID_SELECT, select_click_handler);
  window_single_click_subscribe(BUTTON_ID_UP, up_click_handler);
  window_single_click_subscribe(BUTTON_ID_DOWN, down_click_handler);
}
static void bt_handler(bool connected) {
  // Show current connection state
  if (connected) {
    text_layer_set_text(text_layer, "Vote for current song(Up/Down):");
  } else {
    text_layer_set_text(text_layer, "Disconnected. Check bluetooth connection!");
  }
}

static void window_load(Window *window) {
  //MENU SHIT
  // Here we load the bitmap assets
  s_menu_icons[0] = NULL;
  // And also load the background
  s_background_bitmap = NULL;
  
  // Now we prepare to initialize the menu layer
  Layer *window_layer = window_get_root_layer(window);
  GRect window_bounds = layer_get_frame(window_layer);
  
  // Create the menu layer
  s_menu_layer = menu_layer_create(window_bounds);
  menu_layer_set_callbacks(s_menu_layer, NULL, (MenuLayerCallbacks){
    .get_num_sections = menu_get_num_sections_callback,
    .get_num_rows = menu_get_num_rows_callback,
    .get_header_height = menu_get_header_height_callback,
    .draw_header = menu_draw_header_callback,
    .draw_row = menu_draw_row_callback,
    .select_click = menu_select_callback,
  });
  
  // Bind the menu layer's click config provider to the window for interactivity
//   menu_layer_set_click_config_onto_window(s_menu_layer, window);
  layer_add_child(window_layer, menu_layer_get_layer(s_menu_layer));
//LOGO STUFF

  s_example_bitmap = gbitmap_create_with_resource(RESOURCE_ID_logo);
  s_bitmap_layer = bitmap_layer_create(GRect(0, 35, 144, 110));
  bitmap_layer_set_bitmap(s_bitmap_layer, s_example_bitmap);
  
  
  // Create output TextLayer
  text_layer = text_layer_create(GRect(0, 0, window_bounds.size.w, window_bounds.size.h));
  text_layer_set_text(text_layer, "Up for good, Down for Bad!");
  text_layer_set_text_alignment(text_layer, GTextAlignmentCenter);
  layer_add_child(window_layer, text_layer_get_layer(text_layer));
  layer_add_child(window_get_root_layer(window), bitmap_layer_get_layer(s_bitmap_layer));
  // Show current connection state
  bt_handler(bluetooth_connection_service_peek());
}

static void window_unload(Window *window) {
  // Destroy the menu layer
  menu_layer_destroy(s_menu_layer);

  // Cleanup the menu icons
  for (int i = 0; i < NUM_MENU_ICONS; i++) {
    gbitmap_destroy(s_menu_icons[i]);
  }

  gbitmap_destroy(s_background_bitmap);
}

static void init(void) {
 // Create main Window
  window = window_create();
  window_set_click_config_provider(window, click_config_provider);
  window_set_window_handlers(window, (WindowHandlers) {
      .load = window_load,
    .unload = window_unload,
  });
  window_stack_push(window, true);

  // Subscribe to Bluetooth updates
  bluetooth_connection_service_subscribe(bt_handler);
}

static void deinit(void) {
  // Destroy main Window
  window_destroy(window);
}

int main(void) {
  init();
  app_event_loop();
  deinit();
}