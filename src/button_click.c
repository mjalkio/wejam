#include <pebble.h>

static Window *window;
static TextLayer *text_layer;

static void select_click_handler(ClickRecognizerRef recognizer, void *context) {
  text_layer_set_text(text_layer, "Vote Now!");
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
    text_layer_set_text(text_layer, "Connected, Begin Rating Songs!");
  } else {
    text_layer_set_text(text_layer, "Disconnected. Check bluetooth connection!");
  }
}

static void window_load(Window *window) {
  Layer *window_layer = window_get_root_layer(window);
  GRect window_bounds = layer_get_bounds(window_layer);

  // Create output TextLayer
  text_layer = text_layer_create(GRect(0, 0, window_bounds.size.w, window_bounds.size.h));
  text_layer_set_text(text_layer, "Press a button");
  text_layer_set_text_alignment(text_layer, GTextAlignmentCenter);
  layer_add_child(window_layer, text_layer_get_layer(text_layer));

  // Show current connection state
  bt_handler(bluetooth_connection_service_peek());
}

static void window_unload(Window *window) {
  // Destroy output TextLayer
  text_layer_destroy(text_layer);
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