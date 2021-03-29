<template lang="html">
  <section class="container-fluid plot">
    <h1>{{title}}</h1>
    <div>{{help}}</div>
    <div class="row row-eq-height">
      <div class="col-3">
        <span>Agent Id</span>
        <v-select v-model="agentId" :options="allAgents"></v-select>
        <br/>
        <button class="btn btn-secondary" @click="calculateMatrix">Recalculate Matrix</button>
        <loading class="loading" v-if="loading" :loadingImage="loadingImage"></loading>
      </div>
      <div class="col-9 bot-info" v-if="current_cell.cell_y">
        <div class="row">
          <span class="col-2">bot {{current_cell.cell_y}}</span>
          <span class="col-10">{{current_cell.label_y}}</span>
        </div>
        <div class="row">
          <span class="col-2">bot {{current_cell.cell_x}}</span>
          <span class="col-10">{{current_cell.label_x}}</span>
        </div>
        <div class="row">
          <span class="col-2">similarity: </span>
          <span class="col-10">{{current_cell.similarity.toFixed(2)}}</span>
        </div>
      </div>
    </div>
    <p></p>
    <div class="row row-eq-height">
      <div v-for="(plot, plotIndex) in plots" :plotIndex="plotIndex" class="plot col-3">
        <div v-if="plot.matrix" class="inner">
          <header class="row">
            <div class="col-5">Intents: {{plot.matrix.length}}</div>
            <div class="col-5">{{plot.nlp}} {{plot.match_unit}}</div>
          </header>
          <a-similarity-matrix
            :plotIndex="plotIndex"
            :matrix="plot.matrix"
            :cellSpacing="cellSpacing"
            :color="color"
            @showCellInfo="showCellInfo"
            @showCellDetails="showCellDetails"
          ></a-similarity-matrix>
        </div>
      </div>
    </div>
  </section>
</template>

<script lang='js'>
import * as d3 from 'd3'
import SimilarityMatrix from '@/pages/Report/SimilarityMatrix'
import Loading from '@/components/Loading'
import { illusionistAPI } from '@/utils/rest-config'

export default {
  name: 'agents-similarity-matrix',
  components: {
    'loading': Loading,
    'a-similarity-matrix': SimilarityMatrix
  },
  data () {
    return {
      title: 'Bots similarity matrix within selected agent',
      help: 'Mouseover cells to see similarity between 2 bots. Red is bad, green is good. If all fall in Astound logo theme, it is a good agent',
      cellSpacing: 1,
      showLabels: true,
      loading: false,
      loadingImage: require('@/assets/loading-spinner-green.gif'),
      agentId: this.$route.params.agentId,
      allAgents: [],
      agentPath: '/api/agent',
      plots: [
        { matrix: [], meta: {}, nlp: 'luke', match_unit: 'paragraph' },
        { matrix: [], meta: {}, nlp: 'spacy', match_unit: 'paragraph' },
        { matrix: [], meta: {}, nlp: 'luke', match_unit: 'list' },
        { matrix: [], meta: {}, nlp: 'spacy', match_unit: 'list' }
      ],
      color: 'neva',
      current_cell: {
        cell_y: null,
        cell_x: null,
        subcell_y: null,
        subcell_x: null,
        intention_y: '',
        intention_x: '',
        similarity: 0
      }
    }
  },
  computed: {
  },
  mounted () {
    this.fetchAllAgents()
    this.plotAll()
  },
  watch: {
    colorScale: function () {
      this.plotAll()
    },
    agentId: function (value) {
      this.agentId = value.toString()
      this.$router.push({ name: 'similarity-matrix', params: { agentId: this.agentId } })
      this.plotAll()
    }
  },
  methods: {
    calculateMatrix: function () {
      const vm = this
      const apiPath = '/api/agents_similarity_matrix/update'
      vm.loading = true
      var data = {
        'agent_id': vm.agentId,
        'nlps': ['spacy', 'luke'],
        'match_units': ['list', 'paragraph']
      }
      illusionistAPI
        .post(apiPath, data)
        .then((response) => {
          console.log(response.data.msg)
        })
        .catch((error) => {
          console.error(error)
        })
        .then(() => {
          vm.loading = false
          vm.plotAll()
        })
    },
    plotAll: function () {
      const vm = this
      const pathBase = '/api/agents_similarity_matrix/' + vm.agentId

      vm.plots.forEach(function (plot, index) {
        const apiPath = pathBase + '/' + plot.nlp + '/' + plot.match_unit
        vm.loadMatrix(index, apiPath)
      })
    },
    loadMatrix: function (index, apiPath) {
      const vm = this
      vm.loading = true
      illusionistAPI
        .get(apiPath)
        .then((response) => {
          vm.plots[index].matrix = response.data.matrix
        })
        .catch((e) => {
          console.error(e)
        })
        .then(() => {
          vm.loading = false
        })
    },
    showCellInfo: function (data) {
      this.current_cell = data
      this.highlightRelatedCell(data)
    },
    highlightRelatedCell: function (data) {
      d3.selectAll('.cell')
        .classed('active', false)
        .filter((cell) => {
          return (cell.cell_x === data.cell_x) && (cell.cell_y === data.cell_y)
        })
        .classed('active', true)
    },
    showCellDetails: function (data) {
      // console.table(Object.assign({}, data))
    },
    fetchAllAgents: function () {
      const vm = this
      illusionistAPI
        .get(vm.agentPath, {
          headers: this.requestHeaders
        })
        .then(response => {
          const agents = response.data.objects
          agents.forEach((agent) => {
            vm.allAgents.push(agent.id)
          })
        })
    }
  }
}
</script>

<style scoped lang='sass'>
@import '@/assets/variables.scss'
@import '@/assets/action.sass';

.plot
  .loading img
    width: 200px;
  .bot-info
    height: 4em;
    margin: 1em 0;
    font-size: 0.9em;
  .inner
    box-shadow: $box-shadow;
    padding: 1rem;
    height: 100%;
  header
    line-height: 2rem;
  .similarity-matrix
    margin: 1rem 0;
    width: 100%;
</style>
