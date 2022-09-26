import { Tooltip } from "bootstrap";
import { DirectiveBinding } from "vue";

export const tooltip = {
  mounted(el: Element, binding: DirectiveBinding) {
    new Tooltip(el, { title: binding.value });
  },
  updated(el: Element, binding: DirectiveBinding) {
    if (binding.value !== binding.oldValue) {
      new Tooltip(el, { title: binding.value });
    }
  },
};
