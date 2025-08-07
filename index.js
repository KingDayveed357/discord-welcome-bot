require('dotenv').config();
const { Client, GatewayIntentBits, ChannelType } = require('discord.js');

const client = new Client({
  intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildMembers,
    GatewayIntentBits.GuildMessages
  ]
});

client.once('ready', () => {
  console.log(`✅ Logged in as ${client.user.tag}`);
  console.log(`📊 Bot is in ${client.guilds.cache.size} servers`);
});

// Function to find appropriate welcome channel
function findWelcomeChannel(guild) {
  // Priority order for channel names to look for
  const welcomeChannelNames = [
    'welcome',
    'general',
    'announcements',
    'lobby',
    'main',
    'chat'
  ];
  
  // First, try to find channels by common welcome names
  for (const name of welcomeChannelNames) {
    const channel = guild.channels.cache.find(ch => 
      ch.type === ChannelType.GuildText && 
      ch.name.toLowerCase().includes(name) &&
      ch.permissionsFor(guild.members.me).has(['SendMessages', 'ViewChannel'])
    );
    if (channel) return channel;
  }
  
  // If no common names found, get the first text channel the bot can send to
  const fallbackChannel = guild.channels.cache.find(ch => 
    ch.type === ChannelType.GuildText &&
    ch.permissionsFor(guild.members.me).has(['SendMessages', 'ViewChannel'])
  );
  
  return fallbackChannel;
}

client.on('guildMemberAdd', (member) => {
  const channel = findWelcomeChannel(member.guild);
  
  if (!channel) {
    console.log(`❌ No suitable welcome channel found in guild: ${member.guild.name}`);
    return;
  }
  
  channel.send(`👋 Welcome <@${member.id}> to ${member.guild.name}!`)
    .then(() => {
      console.log(`✅ Welcome message sent in ${member.guild.name} (#${channel.name})`);
    })
    .catch(error => {
      console.error(`❌ Failed to send welcome message in ${member.guild.name}:`, error);
    });
});

// Log when bot joins new servers
client.on('guildCreate', (guild) => {
  console.log(`🆕 Bot added to new server: ${guild.name} (${guild.id})`);
  const welcomeChannel = findWelcomeChannel(guild);
  if (welcomeChannel) {
    console.log(`📍 Will use channel #${welcomeChannel.name} for welcomes`);
  }
});

client.login(process.env.DISCORD_TOKEN);