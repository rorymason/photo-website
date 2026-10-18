// Site settings. Edit these values, then rebuild.
// Anything left empty ('') is simply hidden on the site.

export default {
  name: 'Rory Mason',
  role: 'Interaction designer',
  url: 'https://rorymason.xyz',
  description:
    'Rory Mason is an interaction designer in Berlin, designing research-led digital products.',

  // Homepage intro. The second line is shown in grey.
  intro: 'I design research-led digital products, from the first interview to a tested, finished design.',
  introMuted: 'Studying Interaction Design at CODE University in Berlin, and freelancing on brand and web.',

  // Contact details, shown at the bottom of every page.
  email: 'rory.mason@code.berlin',
  linkedin: 'https://www.linkedin.com/in/rory-mason-b450a22aa/',
  cv: '/files/rory-mason-cv.pdf', // put the PDF in static/files/

  // Discipline tags. Projects refer to these by their key (ux, research and so on).
  // The order here is the order of the filter buttons.
  tags: {
    ux:       { label: 'UX & Product',   icon: 'phone' },
    research: { label: 'Research',       icon: 'search' },
    brand:    { label: 'Brand',          icon: 'sparkle' },
    strategy: { label: 'Strategy',       icon: 'compass' },
    motion:   { label: 'Motion & Photo', icon: 'camera' },
  },

  // Container colours. Projects pick one by name.
  colors: {
    rose:     '#FBE4EC',
    sky:      '#DDEBF6',
    butter:   '#F7EECB',
    lavender: '#E8E2F6',
    peach:    '#FCE4D3',
    mint:     '#DCEFE6',
    grey:     '#F1F1EE',
  },
};
