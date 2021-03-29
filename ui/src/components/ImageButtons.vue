<template>
  <div :data_json="data_json" class="image-buttons">
    <div class="image-button" v-for="(image, index) in data_json" :key="index">
      <figure>
        <a :href="image.url" target="_blank">
          <img v-bind:src="image.src" class="img-thumbnail" v-bind:alt="image.title" />
        </a>
      </figure>
      <button class="btn btn-light btn-sm click-effect" v-on:click="$emit('clickToMessage', image.title)">{{ image.title }}</button>
    </div>
  </div>
</template>

<script>
export default {
  components: {},
  props: {
    data_json: {
      type: Array,
      required: true
    }
  }
}
</script>

<style lang="sass">
@import '@/assets/variables.scss';

.image-buttons
  box-sizing: content-box;
  margin: 1em 0;
  .image-button
    cursor: default;
    display: inline-block;
    border: 0;
    border-radius: 3px;
    font-size: 12px;
    margin: 1em 50px 1em 0;
    box-sizing: content-box;
    position: relative;
    text-align: center;
    &:hover .iframe-preview
      opacity: 1;
    figure
      height: 12em;
      width: 12em;
      vertical-align: middle;
      text-align: center;
      .img-thumbnail
        background-color: transparent;
        height: auto;
        border: 0;
        box-shadow: none;
        cursor: pointer;
        box-shadow: $box-shadow-s;
    button
      text-align: center
</style>
